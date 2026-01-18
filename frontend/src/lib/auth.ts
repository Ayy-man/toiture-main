// Session configuration and getSession helper for iron-session
import { getIronSession, SessionOptions } from "iron-session";
import { cookies } from "next/headers";

// Validate environment variables at module level
if (!process.env.IRON_SESSION_SECRET) {
  throw new Error("IRON_SESSION_SECRET environment variable is required");
}
if (process.env.IRON_SESSION_SECRET.length < 32) {
  throw new Error("IRON_SESSION_SECRET must be at least 32 characters");
}
if (!process.env.APP_PASSWORD) {
  throw new Error("APP_PASSWORD environment variable is required");
}

export interface SessionData {
  isAuthenticated: boolean;
}

export const sessionOptions: SessionOptions = {
  password: process.env.IRON_SESSION_SECRET,
  cookieName: "cortex_auth",
  cookieOptions: {
    secure: process.env.NODE_ENV === "production",
    httpOnly: true,
    sameSite: "lax" as const,
  },
};

export async function getSession() {
  // CRITICAL: Next.js 15 requires await on cookies()
  const cookieStore = await cookies();
  return getIronSession<SessionData>(cookieStore, sessionOptions);
}
