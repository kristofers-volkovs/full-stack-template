import { Link, createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/")({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div>
      <p>Welcome!</p>
      <span>
        This is the index page, if you'd like to access the admin panel then click this
        button {"->"}
      </span>
      <Link to="/admin" className="btn">
        Admin panel
      </Link>
    </div>
  )
}
