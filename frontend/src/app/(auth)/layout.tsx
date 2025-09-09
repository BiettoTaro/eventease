export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-orange-200">
      <div className="w-full max-w-md bg-white p-8 rounded-lg shadow-lg">
        {children}
      </div>
    </div>
  );
}
