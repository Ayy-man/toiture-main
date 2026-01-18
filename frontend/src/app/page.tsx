export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-center py-16 px-8 bg-white dark:bg-black">
        <h1 className="text-4xl font-bold tracking-tight text-black dark:text-zinc-50 mb-4">
          TOITURELV Cortex
        </h1>
        <p className="text-lg text-zinc-600 dark:text-zinc-400 text-center max-w-md">
          AI-powered roofing price estimates
        </p>
        {/* Form component will be added in Plan 02 */}
      </main>
    </div>
  );
}
