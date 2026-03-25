import { createFileRoute } from "@tanstack/react-router"
import useAuth from "../../../hooks/useAuth.ts"

export const Route = createFileRoute("/admin/_app/dashboard")({
  component: RouteComponent,
})

function RouteComponent() {
  const { logout } = useAuth()

  return (
    <>
      <p>Dashboard</p>
      <button type="button" onClick={logout}>
        Logout
      </button>
    </>
  )
}
