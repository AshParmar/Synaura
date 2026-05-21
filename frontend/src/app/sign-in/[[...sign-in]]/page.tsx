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
            colorBackground: "#0a0a0a",
            colorText: "#ffffff",
            colorPrimary: "#2563eb",
            colorInputBackground: "#111111",
            colorInputText: "#ffffff",
            borderRadius: "0.5rem",
          },
          elements: {
            card: "border border-white/10 shadow-2xl",
            headerTitle: "text-white",
            headerSubtitle: "text-gray-400",
            socialButtonsBlockButton: "border border-white/10 text-white hover:bg-white/5",
            formFieldInput: "border border-white/10 bg-[#111] text-white",
            footerActionLink: "text-blue-400 hover:text-blue-300",
          },
        }}
      />
    </main>
  );
}
