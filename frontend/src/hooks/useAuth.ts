import { useMutation, useQuery } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { AxiosError } from "axios"
import { useState } from "react"
import { toast } from "react-toastify"
import { type BodyLogin, LoginService, UsersService } from "../client"

const isLoggedIn = () => {
  const accessToken = localStorage.getItem("access_token")
  const refreshToken = localStorage.getItem("refresh_token")

  return accessToken !== null || refreshToken !== null
}

const useAuth = () => {
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const {
    data: user,
    error: userQueryError,
    status: userQueryStatus,
  } = useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => UsersService.getUserMe(),
    enabled: isLoggedIn(),
    retry: (failureCount, error) => {
      if (error instanceof AxiosError) {
        let status = parseInt(error.code!)
        if (status < 500 && status >= 400) {
          return false
        }
      }
      return !(failureCount >= 3)
    },
    refetchOnMount: false,
    refetchOnReconnect: false,
    refetchOnWindowFocus: false,
  })

  const loginMutation = useMutation({
    mutationFn: async (data: BodyLogin) => await LoginService.login({ body: data }),
    onSuccess: (response) => {
      if (response instanceof AxiosError) {
        throw response
      }
      localStorage.setItem("access_token", response.data.access_token)
      localStorage.setItem("refresh_token", response.data.refresh_token)
      navigate({ to: "/admin" })
    },
    onError: (err) => {
      setError(err.message)
    },
  })

  const logout = async () => {
    const refreshToken = localStorage.getItem("refresh_token")
    if (refreshToken) {
      await LoginService.logout({ headers: { "x-token": refreshToken } })
      localStorage.removeItem("refresh_token")
    }

    localStorage.removeItem("access_token")
    navigate({ to: "/login" })
  }

  if (userQueryStatus === "error") {
    toast.error(
      `An error occurred: ${userQueryError.message}, please contact an administrator.`,
    )
    logout()
  }

  return {
    loginMutation,
    logout,
    error,
    user,
    isLoading: userQueryStatus === "pending",
    resetError: () => setError(null),
  }
}

export { isLoggedIn }
export default useAuth
