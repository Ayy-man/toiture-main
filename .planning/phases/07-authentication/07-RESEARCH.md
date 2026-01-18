# Phase 7: Authentication - Research

**Researched:** 2026-01-18
**Domain:** Simple password gate for Next.js 15 App Router
**Confidence:** HIGH

## Summary

This phase implements a simple shared password gate for an internal tool. The requirement explicitly excludes user accounts, OAuth, or persistent sessions - just a single shared password stored in an environment variable.

The standard approach for this use case is **iron-session** - a lightweight, stateless session library that stores encrypted session data in cookies. This avoids database requirements while providing secure cookie-based authentication. The pattern involves: a login page with a form, a Server Action to validate the password against an env var, middleware to protect routes, and a session cookie to remember authentication state.

**Primary recommendation:** Use iron-session 8.x with Next.js 15 App Router patterns. Store `APP_PASSWORD` and `IRON_SESSION_SECRET` (32+ chars) as environment variables. Implement middleware-based route protection with a simple login form.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| iron-session | ^8.0.1 | Encrypted cookie sessions | Official Next.js recommendation, stateless, no database needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (none needed) | - | - | iron-session handles everything |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| iron-session | jose (JWT) | More manual setup, iron-session abstracts cookie handling |
| iron-session | NextAuth.js | Massive overkill for shared password - designed for user accounts |
| iron-session | HTTP Basic Auth | No custom login UI, browser popup instead of form |

**Installation:**
```bash
pnpm add iron-session
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── app/
│   ├── login/
│   │   ├── page.tsx        # Login form (Server Component)
│   │   └── actions.ts      # Server Action to validate password
│   ├── api/
│   │   └── session/
│   │       └── route.ts    # GET session for client components (optional)
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Protected home page
├── lib/
│   └── auth.ts             # Session config and getSession helper
└── middleware.ts           # Route protection
```

### Pattern 1: Session Configuration
**What:** Centralized session options with typed session data
**When to use:** Always - this is the foundation
**Example:**
```typescript
// src/lib/auth.ts
// Source: https://github.com/vvo/iron-session + https://www.alexchantastic.com/revisiting-password-protecting-next
import { getIronSession, SessionOptions } from "iron-session";
import { cookies } from "next/headers";

export interface SessionData {
  isAuthenticated: boolean;
}

export const sessionOptions: SessionOptions = {
  password: process.env.IRON_SESSION_SECRET!,
  cookieName: "cortex_auth",
  cookieOptions: {
    secure: process.env.NODE_ENV === "production",
    httpOnly: true,
    sameSite: "lax",
  },
};

export async function getSession() {
  // CRITICAL: Next.js 15 requires await on cookies()
  const cookieStore = await cookies();
  return getIronSession<SessionData>(cookieStore, sessionOptions);
}
```

### Pattern 2: Server Action for Login
**What:** Password validation via Server Action
**When to use:** Login form submission
**Example:**
```typescript
// src/app/login/actions.ts
// Source: https://www.alexchantastic.com/revisiting-password-protecting-next
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

  // Invalid password - stay on login page
  redirect(`/login?error=invalid&redirect=${encodeURIComponent(redirectTo)}`);
}
```

### Pattern 3: Middleware Route Protection
**What:** Intercept requests and redirect unauthenticated users
**When to use:** Protect all routes except /login and static assets
**Example:**
```typescript
// src/middleware.ts
// Source: https://nextjs.org/docs/app/guides/authentication
import { NextRequest, NextResponse } from "next/server";
import { getSession } from "@/lib/auth";

export async function middleware(request: NextRequest) {
  const session = await getSession();
  const path = request.nextUrl.pathname;

  // Already on login page - allow
  if (path === "/login") {
    return NextResponse.next();
  }

  // Not authenticated - redirect to login
  if (!session.isAuthenticated) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", path);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  // Protect all routes except static assets and API routes
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api).*)"],
};
```

### Pattern 4: Login Page
**What:** Simple form with Server Action
**When to use:** The /login route
**Example:**
```typescript
// src/app/login/page.tsx
// Source: https://www.alexchantastic.com/revisiting-password-protecting-next
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
    <div className="flex min-h-screen items-center justify-center">
      <form action={authenticate} className="w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-bold text-center">TOITURELV Cortex</h1>
        <p className="text-center text-muted-foreground">Enter password to continue</p>

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
          className="w-full px-3 py-2 border rounded-md"
        />

        <button type="submit" className="w-full py-2 bg-primary text-primary-foreground rounded-md">
          Sign In
        </button>
      </form>
    </div>
  );
}
```

### Anti-Patterns to Avoid
- **Storing password in code:** Never hardcode passwords - always use environment variables
- **Client-side password validation:** Always validate on server via Server Actions
- **Skipping httpOnly on cookies:** Without httpOnly, cookies are accessible to XSS attacks
- **Forgetting await on cookies():** Next.js 15 requires `await cookies()` - synchronous access is deprecated
- **Complex auth for simple needs:** NextAuth.js or OAuth is overkill for a shared password

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cookie encryption | Custom encryption scheme | iron-session | Handles salt, encryption, timing-safe comparison |
| Session management | localStorage + custom API | iron-session cookies | Cookies work server-side, localStorage doesn't |
| Route protection | Manual checks in every page | Next.js middleware | Single point of control, can't forget protection |

**Key insight:** Cookie-based session management involves subtle security considerations (encryption, timing attacks, cookie flags). iron-session handles all of this correctly.

## Common Pitfalls

### Pitfall 1: Synchronous cookies() in Next.js 15
**What goes wrong:** Runtime errors or deprecation warnings when using `cookies()` without await
**Why it happens:** Next.js 15 made dynamic APIs async for performance
**How to avoid:** Always `await cookies()` before passing to getIronSession
**Warning signs:** Console warnings about sync access to dynamic APIs

### Pitfall 2: Missing IRON_SESSION_SECRET
**What goes wrong:** App crashes on startup with cryptic error about password length
**Why it happens:** Forgot to set env var or set one shorter than 32 characters
**How to avoid:** Validate env vars at startup, use clear error messages
**Warning signs:** "Password must be at least 32 characters" error

### Pitfall 3: Middleware Running on Static Assets
**What goes wrong:** Slow page loads, broken images/CSS
**Why it happens:** Middleware matcher is too broad
**How to avoid:** Use explicit matcher config excluding _next/static, _next/image, favicon.ico
**Warning signs:** Network tab shows auth redirects for .js, .css, .png files

### Pitfall 4: Redirect Loop on Login Page
**What goes wrong:** Infinite redirect between / and /login
**Why it happens:** Login page itself is protected by middleware
**How to avoid:** Explicitly exclude /login from middleware matcher or check path
**Warning signs:** Browser shows "too many redirects" error

### Pitfall 5: Safari Cookie Issues
**What goes wrong:** Session not persisted on refresh in Safari
**Why it happens:** Safari has stricter SameSite cookie handling
**How to avoid:** Ensure SameSite is "lax" (not "strict"), test in Safari during development
**Warning signs:** Works in Chrome, fails in Safari

## Code Examples

Verified patterns from official sources:

### Logout Action
```typescript
// src/app/login/actions.ts (add to existing file)
// Source: https://nextjs.org/docs/app/guides/authentication
"use server";
import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";

export async function logout() {
  const session = await getSession();
  session.destroy();
  redirect("/login");
}
```

### Logout Button Component
```typescript
// src/components/logout-button.tsx
"use client";
import { logout } from "@/app/login/actions";

export function LogoutButton() {
  return (
    <form action={logout}>
      <button type="submit" className="text-sm text-muted-foreground hover:underline">
        Sign Out
      </button>
    </form>
  );
}
```

### Environment Variable Validation
```typescript
// src/lib/auth.ts (add at top)
// Source: Best practice
if (!process.env.IRON_SESSION_SECRET) {
  throw new Error("IRON_SESSION_SECRET environment variable is required");
}
if (process.env.IRON_SESSION_SECRET.length < 32) {
  throw new Error("IRON_SESSION_SECRET must be at least 32 characters");
}
if (!process.env.APP_PASSWORD) {
  throw new Error("APP_PASSWORD environment variable is required");
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| withIronSession wrapper | getIronSession() direct | iron-session v8 (Nov 2024) | Simpler API, App Router native |
| cookies() sync | await cookies() | Next.js 15 (Oct 2024) | Must await before passing to getIronSession |
| Pages Router middleware | App Router middleware | Next.js 13+ | Different file location, async by default |

**Deprecated/outdated:**
- `next-iron-session` package - Use `iron-session` directly
- `withIronSessionApiRoute` wrapper - Use `getIronSession()` instead
- Synchronous `cookies()` - Must use await in Next.js 15

## Open Questions

Things that couldn't be fully resolved:

1. **Session TTL preference**
   - What we know: iron-session defaults to 14 days, can be set to any value
   - What's unclear: Whether user wants sessions to expire (for security) or persist indefinitely (convenience)
   - Recommendation: Use 7-day TTL as reasonable default for internal tool

## Sources

### Primary (HIGH confidence)
- [iron-session GitHub](https://github.com/vvo/iron-session) - v8.0.1 API, SessionOptions interface
- [Next.js Authentication Guide](https://nextjs.org/docs/app/guides/authentication) - Session patterns, middleware, cookies
- [Alex Chan's Tutorial](https://www.alexchantastic.com/revisiting-password-protecting-next) - Complete iron-session + Next.js 15 example

### Secondary (MEDIUM confidence)
- [Next.js 15 Release Notes](https://nextjs.org/blog/next-15) - async cookies() breaking change
- [iron-session Releases](https://github.com/vvo/iron-session/releases) - v8.0.1 release notes

### Tertiary (LOW confidence)
- [GitHub Discussions #870](https://github.com/vvo/iron-session/issues/870) - Safari cookie issue (may be edge case)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - iron-session is officially recommended by Next.js docs
- Architecture: HIGH - Patterns verified against official docs and working examples
- Pitfalls: HIGH - Well-documented in Next.js 15 migration guides

**Research date:** 2026-01-18
**Valid until:** 2026-03-18 (60 days - mature stack, stable patterns)
