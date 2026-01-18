"use client";

import { logout } from "@/app/login/actions";

export function LogoutButton() {
  return (
    <form action={logout}>
      <button
        type="submit"
        className="text-sm text-zinc-500 hover:underline"
      >
        Sign Out
      </button>
    </form>
  );
}
