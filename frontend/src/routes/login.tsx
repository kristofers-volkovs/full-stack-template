import { zodResolver } from "@hookform/resolvers/zod"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"
import { z } from "zod"
import PasswordLoginIcon from "../components/icons/PasswordLoginIcon.tsx"
import UserLoginIcon from "../components/icons/UserLoginIcon.tsx"
import useAuth, { isLoggedIn } from "../hooks/useAuth.ts"

export const Route = createFileRoute("/login")({
  component: RouteComponent,
  validateSearch: z.object({ redirect: z.string().optional().catch("") }),
  beforeLoad: async ({ search }) => {
    if (isLoggedIn()) {
      throw redirect({ to: search.redirect || "/admin" })
    }
  },
})

const loginSchema = z.object({
  username: z
    .string({ required_error: "Email is required" })
    .email("Invalid email format"),
  password: z
    .string({ required_error: "Password is required" })
    .min(8, "Password must be at least 8 characters"),
})
type LoginFormType = z.infer<typeof loginSchema>

function RouteComponent() {
  const { loginMutation, error, resetError } = useAuth()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormType>({ resolver: zodResolver(loginSchema) })

  const onSubmit: SubmitHandler<LoginFormType> = async (data) => {
    if (isSubmitting) return
    resetError()
    try {
      await loginMutation.mutateAsync(data)
    } catch (error) {
      // error is handled by useAuth hook
    }
  }

  return (
    <div className="w-full h-dvh flex flex-col items-center justify-center">
      <div>
        <h1>Logo</h1>
      </div>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <label className="input validator">
            <UserLoginIcon />
            <input type="email" {...register("username")} placeholder="Email" />
          </label>
          {errors.username && <p>{errors.username?.message}</p>}
        </div>
        <div>
          <label className="input validator">
            <PasswordLoginIcon />
            <input type="password" {...register("password")} placeholder="Password" />
          </label>
          {errors.password && <p>{errors.password?.message}</p>}
        </div>
        {error && <p>{error}</p>}
        <div>
          <button className="btn" type="submit">
            Login
          </button>
        </div>
      </form>
    </div>
  )
}
