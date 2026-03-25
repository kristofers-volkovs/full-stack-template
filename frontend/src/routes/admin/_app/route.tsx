import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"
import useAuth, { isLoggedIn } from "../../../hooks/useAuth.ts"

export const Route = createFileRoute("/admin/_app")({
  component: RouteComponent,
  beforeLoad: async ({ location }) => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
        search: { redirect: location.href },
      })
    }
  },
})

function RouteComponent() {
  const { isLoading } = useAuth()

  return (
    <div>
      <p>Sidebar</p>
      {isLoading ? (
        <div className="w-full h-dvh flex flex-col justify-center items-center">
          <span className="loading loading-spinner loading-xl" />
        </div>
      ) : (
        <Outlet />
      )}
      <p>UserMenu</p>
    </div>
  )
}
