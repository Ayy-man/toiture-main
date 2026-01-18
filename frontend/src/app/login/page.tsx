import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";
import { authenticate } from "./actions";

interface Props {
  searchParams: Promise<{ redirect?: string; error?: string }>;
}

export default async function LoginPage({ searchParams }: Props) {
  const session = await getSession();
  const params = await searchParams;

  // Already authenticated - go home
  if (session.isAuthenticated) {
    redirect("/");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <form action={authenticate} className="w-full max-w-sm space-y-4 px-4">
        <h1 className="text-3xl font-bold tracking-tight text-black dark:text-zinc-50 text-center">
          TOITURELV Cortex
        </h1>
        <p className="text-center text-zinc-600 dark:text-zinc-400">
          Enter password to continue
        </p>

        <input type="hidden" name="redirect" value={params.redirect || "/"} />

        {params.error && (
          <p className="text-sm text-red-500 text-center">Invalid password</p>
        )}

        <input
          name="password"
          type="password"
          placeholder="Password"
          required
          autoFocus
          className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-md bg-white dark:bg-zinc-900 text-black dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-zinc-500"
        />

        <button
          type="submit"
          className="w-full py-2 bg-zinc-900 dark:bg-zinc-50 text-zinc-50 dark:text-zinc-900 rounded-md font-medium hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-colors"
        >
          Sign In
        </button>
      </form>
    </div>
  );
}
