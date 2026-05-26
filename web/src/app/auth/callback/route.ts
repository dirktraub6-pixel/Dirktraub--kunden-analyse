import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const code = searchParams.get("code");
  const error = searchParams.get("error");
  const origin = request.nextUrl.origin;

  if (error) {
    const description = searchParams.get("error_description") || "";
    const reason = description.includes("expired") ? "expired" : "invalid";
    return NextResponse.redirect(`${origin}/auth/login?error=${reason}`);
  }

  if (!code) {
    return NextResponse.redirect(`${origin}/auth/login?error=auth`);
  }

  const supabase = await createClient();
  const { error: exchangeError } =
    await supabase.auth.exchangeCodeForSession(code);

  if (exchangeError) {
    return NextResponse.redirect(`${origin}/auth/login?error=auth`);
  }

  return NextResponse.redirect(`${origin}/dashboard`);
}
