import { getSession } from "@/lib/auth";
import { redirect } from "next/navigation";
import { authenticate } from "./actions";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Home } from "lucide-react";

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
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Home className="h-6 w-6" />
          </div>
          <CardTitle className="text-2xl">TOITURELV Cortex</CardTitle>
          <CardDescription>Enter password to continue</CardDescription>
        </CardHeader>
        <CardContent>
          <form action={authenticate} className="space-y-4">
            <input type="hidden" name="redirect" value={params.redirect || "/"} />

            {params.error && (
              <p className="text-sm text-destructive text-center">Invalid password</p>
            )}

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                autoFocus
              />
            </div>

            <Button type="submit" className="w-full">
              Sign In
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
