import { Link } from "@tanstack/react-router"

const NotFound = () => {
  return (
    <>
      <div className="w-full h-dvh flex flex-col justify-center">
        <div className="text-center">
          <div className="pb-5">
            <p className="text-9xl">404</p>
            <p className="text-xl">Page not found</p>
          </div>
          <Link className="btn" to="/">
            Go back
          </Link>
        </div>
      </div>
    </>
  )
}

export default NotFound
