import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-full flex-1 flex-col items-center justify-center bg-zinc-950 px-4">
      <div className="max-w-lg text-center">
        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
          Soul Mastery
        </h1>
        <p className="mt-4 text-lg text-zinc-400">
          Dein Raum fuer persoenliches Wachstum und Transformation. Entdecke
          dein volles Potenzial mit individueller Begleitung.
        </p>
        <div className="mt-8">
          <Link
            href="/auth/login"
            className="inline-flex items-center rounded-lg bg-indigo-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-zinc-950"
          >
            Zum Login
          </Link>
        </div>
      </div>
    </div>
  );
}
