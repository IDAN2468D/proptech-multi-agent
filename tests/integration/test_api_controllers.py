import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.dal.sql.database import init_sql_db
from app.main import app


@pytest.mark.asyncio
async def test_full_end_to_end_api_and_hitl_workflow():
    await init_sql_db()
    unique_email = f"investor_{uuid.uuid4().hex[:8]}@proptech.co.il"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Register User
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "full_name": "דניאל כהן - משקיע נדל\"ן",
                "password": "StrongPassword123!",
            },
        )
        assert reg_resp.status_code == 201
        user_data = reg_resp.json()
        assert user_data["email"] == unique_email

        # 2. Login & obtain JWT
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "StrongPassword123!"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get & Update Investor Long-Term Memory Profile
        prof_get = await client.get("/api/v1/investor/profile", headers=headers)
        assert prof_get.status_code == 200
        assert prof_get.json()["available_equity_ils"] == 800000.0

        prof_put = await client.put(
            "/api/v1/investor/profile",
            headers=headers,
            json={
                "available_equity_ils": 1_100_000.0,
                "risk_tolerance": "MODERATE",
                "max_risk_score_threshold": 70,
                "min_target_net_yield_pct": 3.0,
                "preferred_cities": ["חיפה", "רמת גן"],
                "is_single_home_buyer": True,
            },
        )
        assert prof_put.status_code == 200
        assert prof_put.json()["available_equity_ils"] == 1_100_000.0

        # 4. Create a risky property with a Tabu warning note & area clash -> triggers 202 HITL
        prop_resp = await client.post(
            "/api/v1/properties",
            headers=headers,
            json={
                "address": "שדרות הנשיא 45",
                "city": "חיפה",
                "neighborhood": "מרכז הכרמל",
                "asking_price_ils": 1_900_000.0,
                "area_sqm": 105.0,
                "rooms": 4.0,
                "floor": 3,
                "estimated_monthly_rent_ils": 6800.0,
                "is_single_home": True,
            },
        )
        assert prop_resp.status_code == 201
        property_id = prop_resp.json()["id"]

        # 5. Upload PDF Document with Tabu area 80 sqm (vs 105 sqm in listing) & warning note
        pdf_content = (
            "[PAGE 1] לשכת רישום המקרקעין חיפה. נסח טאבו גוש 10820 חלקה 17. "
            "שטח הדירה הרשום בטאבו: 80 מ\"ר. "
            "[PAGE 2] רשומה הערת אזהרה לפי סעיף 126 לחוק המקרקעין וכן עיקול זמני."
        ).encode("utf-8")

        doc_resp = await client.post(
            f"/api/v1/properties/{property_id}/documents",
            headers=headers,
            files={"file": ("tabu_haifa.pdf", pdf_content, "application/pdf")},
        )
        assert doc_resp.status_code == 201
        doc_json = doc_resp.json()
        assert doc_json["chunks_indexed"] >= 2
        assert doc_json["pages_extracted"] == 2

        # 6. Run Multi-Agent Analysis -> Expect 202 Accepted (PAUSED_FOR_APPROVAL)
        run_resp = await client.post(
            "/api/v1/analysis/run",
            headers=headers,
            json={
                "property_id": property_id,
                "equity_ils": 1_100_000.0,
                "annual_interest_rate_pct": 4.75,
                "loan_years": 25,
            },
        )
        assert run_resp.status_code == 202
        run_data = run_resp.json()
        assert run_data["status"] == "PAUSED_FOR_APPROVAL"
        assert run_data["critic"]["status"] == "NEEDS_HUMAN_REVIEW"
        assert run_data["critic"]["math_verification_passed"] is True
        assert run_data["legal"]["has_blocking_liens_or_warnings"] is True
        assert run_data["legal"]["registered_area_sqm"] == 80.0
        assert len(run_data["critic"]["context_clashes_detected"]) >= 1
        run_id = run_data["run_id"]

        # 7. Approve HITL after renegotiating price down to 1,650,000 ILS
        approve_resp = await client.post(
            f"/api/v1/analysis/{run_id}/approve",
            headers=headers,
            json={
                "approved": True,
                "updated_asking_price_ils": 1_650_000.0,
                "updated_equity_ils": 1_100_000.0,
                "investor_notes": "המוכר המציא מכתב החרגה והוריד מחיר ב-250 אלף ש\"ח בגין פער השטח.",
            },
        )
        assert approve_resp.status_code == 200
        approved_report = approve_resp.json()
        assert approved_report["status"] == "COMPLETED"
        assert approved_report["critic"]["status"] == "APPROVED"
        # Loan amount is now 1,650,000 - 1,100,000 = 550,000 ILS
        assert approved_report["financials"]["loan_amount_ils"] == 550_000.0

        # 8. Retrieve final report by run_id
        get_run_resp = await client.get(f"/api/v1/analysis/{run_id}", headers=headers)
        assert get_run_resp.status_code == 200
        assert get_run_resp.json()["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_centralized_error_manager_standardized_envelope():
    await init_sql_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Missing JWT -> 401 with standardized error envelope & trace_id
        unauth = await client.get("/api/v1/investor/profile")
        assert unauth.status_code == 401
        err_body = unauth.json()
        assert err_body["success"] is False
        assert err_body["error"]["code"] == "AUTH_UNAUTHORIZED"
        assert "trace_id" in err_body["error"]



@pytest.mark.asyncio
async def test_v2_expansion_pack_9_agents_and_new_endpoints():
    await init_sql_db()
    unique_email = f"investor_v2_{uuid.uuid4().hex[:8]}@proptech.co.il"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "full_name": "משקיע גרסה 2",
                "password": "StrongPassword123!",
            },
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": unique_email, "password": "StrongPassword123!"},
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        prop_resp = await client.post(
            "/api/v1/properties",
            headers=headers,
            json={
                "address": "ארלוזורוב 18",
                "city": "רמת גן",
                "neighborhood": "הבורסה",
                "asking_price_ils": 2_400_000.0,
                "area_sqm": 95.0,
                "rooms": 3.5,
                "floor": 2,
                "estimated_monthly_rent_ils": 7_800.0,
                "is_single_home": True,
            },
        )
        property_id = prop_resp.json()["id"]

        # 1. Test POST /api/v1/properties/{id}/vision-upload
        vision_resp = await client.post(
            f"/api/v1/properties/{property_id}/vision-upload",
            headers=headers,
            data={
                "property_condition_hint": "NEEDS_COSMETIC_RENOVATION",
                "has_dampness_hint": "true",
            },
        )
        assert vision_resp.status_code == 200
        v_data = vision_resp.json()
        assert v_data["total_estimated_renovation_ils"] > 0
        assert len(v_data["boq_items"]) >= 3

        # 2. Run 9-Agent Pipeline
        run_resp = await client.post(
            "/api/v1/analysis/run",
            headers=headers,
            json={
                "property_id": property_id,
                "equity_ils": 1_300_000.0,
                "annual_interest_rate_pct": 4.70,
                "loan_years": 25,
            },
        )
        assert run_resp.status_code in (200, 202)
        report = run_resp.json()
        run_id = report["run_id"]

        # Assert all 4 new v2.0 Agent outputs are present in report
        assert report["vision_renovation"] is not None
        assert report["urban_renewal_gis"] is not None
        assert report["macro_stress_test"] is not None
        assert report["negotiation_playbook"] is not None
        assert report["negotiation_playbook"]["target_closing_price_ils"] < 2_400_000.0

        # 3. Test POST /api/v1/analysis/{run_id}/stress-test (Interactive What-If Sandbox)
        stress_resp = await client.post(
            f"/api/v1/analysis/{run_id}/stress-test",
            headers=headers,
            json={
                "interest_rate_pct": 5.9,
                "monthly_rent_ils": 7_200.0,
                "renovation_overrun_ils": 50_000.0,
            },
        )
        assert stress_resp.status_code == 200
        assert "probability_of_positive_cashflow_pct" in stress_resp.json()

        # 4. Test POST /api/v1/analysis/{run_id}/share-deal (Deal-Room Comms MCP)
        share_resp = await client.post(
            f"/api/v1/analysis/{run_id}/share-deal",
            headers=headers,
            json={"webhook_channel": "#investments-il"},
        )
        assert share_resp.status_code == 200
        share_data = share_resp.json()
        assert share_data["dispatched"] is True
        assert "BEGIN:VCALENDAR" in share_data["calendar_ics"]
