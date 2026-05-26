"use server";

import { redirect } from "next/navigation";
import { headers } from "next/headers";
import { createClient } from "@/lib/supabase/server";

type AuthState = {
  error?: string;
  success?: string;
};

const rateLimitMap = new Map<string, { count: number; resetAt: number }>();

const RATE_LIMIT_MAX = 3;
const RATE_LIMIT_WINDOW_MS = 5 * 60 * 1000;

function checkRateLimit(email: string): boolean {
  const now = Date.now();
  const entry = rateLimitMap.get(email);

  if (!entry || now > entry.resetAt) {
    rateLimitMap.set(email, { count: 1, resetAt: now + RATE_LIMIT_WINDOW_MS });
    return true;
  }

  if (entry.count >= RATE_LIMIT_MAX) {
    return false;
  }

  entry.count++;
  return true;
}

export async function sendMagicLink(
  prevState: AuthState | undefined,
  formData: FormData,
): Promise<AuthState> {
  const email = formData.get("email") as string;

  if (!email || typeof email !== "string") {
    return { error: "Bitte gib eine E-Mail-Adresse ein." };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { error: "Bitte gib eine gueltige E-Mail-Adresse ein." };
  }

  if (!checkRateLimit(email.toLowerCase())) {
    return {
      error:
        "Zu viele Anfragen. Bitte warte ein paar Minuten und versuche es erneut.",
    };
  }

  const headersList = await headers();
  const baseUrl =
    process.env.NEXT_PUBLIC_SITE_URL ||
    `https://${headersList.get("host") || "localhost:3000"}`;

  const supabase = await createClient();

  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: `${baseUrl}/auth/callback`,
    },
  });

  if (error) {
    return { error: "Etwas ist schiefgelaufen. Bitte versuche es erneut." };
  }

  return { success: "Check deine E-Mail!" };
}

export async function signOut(): Promise<void> {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/auth/login");
}
