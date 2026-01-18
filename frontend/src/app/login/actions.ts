"use server";

import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";

export async function authenticate(formData: FormData) {
  const session = await getSession();
  const password = formData.get("password") as string;
  const redirectTo = (formData.get("redirect") as string) || "/";

  // Compare against env var
  if (password === process.env.APP_PASSWORD) {
    session.isAuthenticated = true;
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
