"use client";

import { useState } from "react";

type AuthFormProps = {
  mode: "login" | "signup";
  onSubmitAction: (data: { email: string; password: string; name?: string }) => Promise<void>;
  error?: string | null;
};

export default function AuthForm({ mode, onSubmitAction, error }: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmitAction({ email, password, name });
  };

  return (
    <div className="p-8 rounded-lg shadow-md w-full max-w-md">
      <h2 className="text-2xl font-bold mb-6 text-center">
        {mode === "login" ? "Login" : "Sign Up"}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {mode === "signup" && (
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-2 border rounded-md "
            required
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded-md "
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 border rounded-md "
          required
        />
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <button
          type="submit"
          className="w-full bg-orange-500 text-white py-2 rounded-md hover:bg-orange-600 transition"
        >
          {mode === "login" ? "Sign In" : "Create Account"}
        </button>
      </form>
    </div>
  );
}
