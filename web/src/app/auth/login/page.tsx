"use client";

import { Suspense } from "react";
import { useActionState } from "react";
import { useSearchParams } from "next/navigation";
import { sendMagicLink } from "@/app/actions/auth";

const ERROR_MESSAGES: Record<string, string> = {
  expired: "Dein Login-Link ist abgelaufen. Fordere einen neuen an.",
  invalid: "Der Login-Link ist ungueltig. Fordere einen neuen an.",
  auth: "Anmeldung fehlgeschlagen. Bitte versuche es erneut.",
};

function LoginForm() {
  const [state, formAction, pending] = useActionState(
    sendMagicLink,
    undefined,
  );
  const searchParams = useSearchParams();
  const callbackError = searchParams.get("error");

  return (
    <div className="flex min-h-full flex-1 flex-col items-center justify-center bg-zinc-950 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            Soul Mastery
          </h1>
          <p className="mt-2 text-sm text-zinc-400">
            Melde dich an, um fortzufahren
          </p>
        </div>

        {callbackError && ERROR_MESSAGES[callbackError] && (
          <div className="mb-4 rounded-lg border border-red-800 bg-red-950 p-3 text-sm text-red-300">
            {ERROR_MESSAGES[callbackError]}
          </div>
        )}

        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 shadow-lg">
          {state?.success ? (
            <div className="text-center">
              <div className="mb-3 text-3xl">&#9993;</div>
              <h2 className="text-lg font-medium text-white">
                {state.success}
              </h2>
              <p className="mt-2 text-sm text-zinc-400">
                Wir haben dir einen Magic Link gesendet. Klicke auf den Link in
                deiner E-Mail, um dich anzumelden.
              </p>
            </div>
          ) : (
            <form action={formAction} className="space-y-4">
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-zinc-300"
                >
                  E-Mail-Adresse
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  autoComplete="email"
                  placeholder="deine@email.de"
                  className="mt-1.5 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-white placeholder-zinc-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              {state?.error && (
                <p className="text-sm text-red-400" aria-live="polite">
                  {state.error}
                </p>
              )}

              <button
                type="submit"
                disabled={pending}
                className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-zinc-900 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {pending ? "Wird gesendet..." : "Magic Link senden"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
