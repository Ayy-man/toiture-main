import { EstimateForm } from "@/components/estimate-form";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="container mx-auto max-w-2xl py-8 px-4">
        <h1 className="text-4xl font-bold tracking-tight text-black dark:text-zinc-50 mb-4 text-center">
          TOITURELV Cortex
        </h1>
        <p className="text-lg text-zinc-600 dark:text-zinc-400 text-center max-w-md mx-auto mb-8">
          AI-powered roofing price estimates
        </p>
        <EstimateForm />
      </main>
    </div>
  );
}
