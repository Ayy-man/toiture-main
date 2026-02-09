"use server";

import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";

export async function authenticate(formData: FormData) {
  const session = await getSession();
  const password = formData.get("password") as string;
  const username = (formData.get("username") as string) || "estimateur";
  const redirectTo = (formData.get("redirect") as string) || "/";

  // Compare against env var
  if (password === process.env.APP_PASSWORD) {
    session.isAuthenticated = true;

    // Set username for audit trail
    session.username = username;

    // Determine role based on ADMIN_USERS env var
    const adminUsers = process.env.ADMIN_USERS?.split(',').map(u => u.trim().toLowerCase()) || [];
    const isAdmin = adminUsers.includes(username.toLowerCase());
    session.role = isAdmin ? 'admin' : 'estimator';

    await session.save();
    redirect(redirectTo.startsWith("/") ? redirectTo : "/");
  }

  // Invalid password - stay on login page with error
  redirect(`/login?error=invalid&redirect=${encodeURIComponent(redirectTo)}`);
}

export async function logout() {
  const session = await getSession();
  session.destroy();
  redirect("/login");
}
