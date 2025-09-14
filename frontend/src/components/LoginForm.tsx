"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { login as loginApi } from "../lib/api";

interface LoginFormData {
  email: string;
  password: string;
}

export default function LoginForm() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    try {
      const res = await loginApi(data.email, data.password);

      // Save token in localStorage
      localStorage.setItem("token", res.access_token);

      // Redirect to home
      router.push("/home");
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <div className="w-full max-w-md space-y-8">
      <div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-orange-500">
          Sign in to your account
        </h2>
      </div>
      <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
        <div className="rounded-md shadow-sm space-y-4">
          {/* Email */}
          <div>
            <label htmlFor="email" className="sr-only">
              Email address
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              className="label"
              placeholder="Email address"
              {...register("email", {
                required: "Email is required",
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: "Invalid email address",
                },
              })}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="sr-only">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              className="label"
              placeholder="Password"
              {...register("password", {
                required: "Password is required",
                minLength: {
                  value: 6,
                  message: "Password must be at least 6 characters",
                },
              })}
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>
        </div>

        {/* Remember me + Register */}
        <div className="flex items-center justify-between">
          {/* <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="h-4 w-4 focus:ring-orange-400 border-gray-300 rounded"
            />
            <label
              htmlFor="remember-me"
              className="ml-2 block text-sm text-orange-500"
            >
              Remember me
            </label>
          </div> */}

          <div className="flex items-center gap-2 text-sm">
            <p
            className="text-orange-500"
            >Don&apos;t have an account?</p>
            <a
              href="/signup"
              className="font-medium text-indigo-600 hover:text-indigo-500"
            >
              Register
            </a>
          </div>
        </div>

        {/* Submit */}
        <div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent
             text-sm font-medium rounded-md text-white bg-orange-500
              hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-offset-2
               focus:ring-orange-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </div>
      </form>
    </div>
  );
}
