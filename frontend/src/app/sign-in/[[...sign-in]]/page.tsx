// frontend/src/app/sign-in/[[...sign-in]]/page.tsx
// Clerk hosted sign-in page.
// The [[...sign-in]] catch-all route is required by Clerk.

import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <main className="min-h-screen bg-black flex items-center justify-center">
      {/* Dark appearance matches Synaura's design system */}
      <SignIn
        appearance={{
          variables: {
            colorBackground: "#ffffff",
            colorText: "#0f172a",
            colorPrimary: "#000000",
            colorInputBackground: "#ffffff",
            colorInputText: "#0f172a",
            borderRadius: "0.5rem",
          },
          elements: {
            card: "border border-black/5 shadow-2xl",
            headerTitle: "text-slate-900",
            headerSubtitle: "text-slate-500",
            socialButtonsBlockButton: "border border-slate-200 text-slate-900 hover:bg-slate-50",
            formFieldInput: "border border-slate-200 bg-white text-slate-900",
            footerActionLink: "text-blue-600 hover:text-blue-700",
          },
        }}
      />
    </main>
  );
}
