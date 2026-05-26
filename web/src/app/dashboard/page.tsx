import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { signOut } from "@/app/actions/auth";

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/auth/login");
  }

  return (
    <div className="flex min-h-full flex-1 flex-col bg-zinc-950">
      <header className="border-b border-zinc-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <h1 className="text-lg font-semibold text-white">Soul Mastery</h1>
          <form action={signOut}>
            <button
              type="submit"
              className="rounded-lg border border-zinc-700 px-4 py-1.5 text-sm text-zinc-300 transition-colors hover:border-zinc-600 hover:text-white"
            >
              Abmelden
            </button>
          </form>
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-12">
        <h2 className="text-2xl font-semibold text-white">Willkommen</h2>
        <p className="mt-2 text-zinc-400">
          Angemeldet als{" "}
          <span className="font-medium text-zinc-200">{user.email}</span>
        </p>
      </main>
    </div>
  );
}
