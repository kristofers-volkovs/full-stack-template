export const STATUS_ERROR_MESSAGES: Record<number, string> = {
  401: "You are not authorized. Please log in.",
  403: "You do not have permission to perform this action.",
  500: "An unexpected error occurred. Please try again later.",
}

export const GENERIC_ERROR_MESSAGE = {
  GENERIC_ERROR: "Something went wrong. Please try again.",
  AUTHORIZATION_ERROR: "Authorization expired. Please log in again.",
  NETWORK_ERROR:
    "Network error, unable to connect to the server. Please check your connection.",
}
