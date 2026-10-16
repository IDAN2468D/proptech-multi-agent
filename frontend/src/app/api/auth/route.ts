import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  const token = body?.access_token;

  if (!token) {
    return NextResponse.json(
      { error: "Missing access_token" },
      { status: 400 }
    );
  }

  const response = NextResponse.json({ ok: true });
  response.cookies.set("proptech_token", token, {
    httpOnly: false,
    path: "/",
    maxAge: 3600,
    sameSite: "lax",
  });
  return response;
}

export async function DELETE() {
  const response = NextResponse.json({ ok: true });
  response.cookies.delete("proptech_token");
  return response;
}
