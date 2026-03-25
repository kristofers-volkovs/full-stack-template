import { createFileRoute, redirect } from "@tanstack/react-router"
import { z } from "zod"
import { isLoggedIn } from "../../hooks/useAuth.ts"

export const Route = createFileRoute("/admin/")({
  component: RouteComponent,
  validateSearch: z.object({ redirect: z.string().optional().catch("") }),
  beforeLoad: async ({ search, location }) => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
        search: { redirect: location.href },
      })
    }
    throw redirect({
      to: search.redirect || "/admin/dashboard",
    })
  },
})

function RouteComponent() {
  return <></>
}
