/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000"}/:path*`,
      },
    ];
  },
  env: {
    // Clerk redirect paths — must match the file structure in src/app/
    NEXT_PUBLIC_CLERK_SIGN_IN_URL: "/sign-in",
    NEXT_PUBLIC_CLERK_SIGN_UP_URL: "/sign-up",
    NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL: "/demo",
    NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL: "/demo",
  },
};

export default nextConfig;
