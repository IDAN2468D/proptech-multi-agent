import { z } from "zod";

export const LoginRequestSchema = z.object({
  email: z.string().email("כתובת אימייל לא תקינה"),
  password: z.string().min(8, "סיסמה חייבת להכיל לפחות 8 תווים"),
});

export const RegisterRequestSchema = z.object({
  email: z.string().email("כתובת אימייל לא תקינה"),
  full_name: z.string().min(2, "שם מלא חייב להכיל לפחות 2 תווים"),
  password: z.string().min(8, "סיסמה חייבת להכיל לפחות 8 תווים"),
});

export const TokenResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string().default("bearer"),
  user_id: z.string(),
  email: z.string(),
});

export const UserResponseSchema = z.object({
  id: z.string(),
  email: z.string(),
  full_name: z.string(),
  is_active: z.boolean(),
});

export type LoginRequest = z.infer<typeof LoginRequestSchema>;
export type RegisterRequest = z.infer<typeof RegisterRequestSchema>;
export type TokenResponse = z.infer<typeof TokenResponseSchema>;
export type UserResponse = z.infer<typeof UserResponseSchema>;
