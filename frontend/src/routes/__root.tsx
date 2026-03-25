import { Outlet, createRootRoute } from "@tanstack/react-router"
import axios, { AxiosError } from "axios"
import React, { Suspense } from "react"
import { ToastContainer, TypeOptions, toast } from "react-toastify"
import { client } from "../client/client.gen.ts"
import NotFound from "../components/common/NotFound.tsx"
import { GENERIC_ERROR_MESSAGE, STATUS_ERROR_MESSAGES } from "../config/customErrors.ts"
import { router } from "../main.tsx"

const loadDevtools = () =>
  Promise.all([
    import("@tanstack/router-devtools"),
    import("@tanstack/react-query-devtools"),
  ]).then(([routerDevTools, reactQueryDevtools]) => {
    return {
      default: () => (
        <>
          <routerDevTools.TanStackRouterDevtools />
          <reactQueryDevtools.ReactQueryDevtools />
        </>
      ),
    }
  })

const TanStackDevtools =
  import.meta.env.NODE_ENV === "production" ? () => null : React.lazy(loadDevtools)

client.setConfig({
  baseURL: import.meta.env.VITE_BACKEND_HOST,
  auth: async () => localStorage.getItem("access_token") || "",
})

client.instance.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<any, any>) => {
    if (!error.response) {
      toast.error(GENERIC_ERROR_MESSAGE.NETWORK_ERROR)
      return Promise.reject(new AxiosError(GENERIC_ERROR_MESSAGE.NETWORK_ERROR))
    }

    const { status, data } = error.response

    if (status === 401) {
      const originalRequest = error.config
      if (originalRequest) {
        try {
          const refreshToken = localStorage.getItem("refresh_token")!
          const response = await axios.post(
            "/api/v1/refresh",
            {},
            {
              baseURL: import.meta.env.VITE_BACKEND_HOST,
              headers: { "x-token": refreshToken },
            },
          )

          const { access_token: accessToken, refresh_token: newRefreshToken } =
            response.data!
          localStorage.setItem("access_token", accessToken)
          localStorage.setItem("refresh_token", newRefreshToken)

          return client.instance(originalRequest)
        } catch (refreshError) {
          console.error("An error occurred:", error)
          console.error("Token refresh failed:", refreshError)

          const accessToken = localStorage.getItem("access_token")
          if (accessToken) {
            localStorage.removeItem("access_token")
            localStorage.removeItem("refresh_token")
          }

          router.navigate({ to: "/login" })

          toast.error(GENERIC_ERROR_MESSAGE.AUTHORIZATION_ERROR)
          return Promise.reject(
            new AxiosError(GENERIC_ERROR_MESSAGE.AUTHORIZATION_ERROR, String(status)),
          )
        }
      }
    }

    const errMessage: string =
      data?.message ||
      STATUS_ERROR_MESSAGES[status] ||
      GENERIC_ERROR_MESSAGE.GENERIC_ERROR
    console.error("An error occurred:", error)

    return Promise.reject(new AxiosError(errMessage, String(status)))
  },
)

export const Route = createRootRoute({
  component: () => <RootComponent />,
  notFoundComponent: () => <NotFound />,
})

function RootComponent() {
  return (
    <>
      <Outlet />
      <ToastContainer position="bottom-right" />
      <Suspense>
        <TanStackDevtools />
      </Suspense>
    </>
  )
}
