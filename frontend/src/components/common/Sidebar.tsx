import { Link } from "@tanstack/react-router"

const Sidebar = () => {
  return (
    <>
      <div className="sidebar fixed top-0 bottom-0 lg:left-0 p-2 w-[300px] overflow-y-auto text-center bg-gray-900">
        <div className="p-2.5 mt-1 flex items-center">
          <h1 className="font-bold text-gray-200 text-[30px] ml-2">Logo</h1>
        </div>
        <div className="my-2 bg-gray-600 h-[1px]" />
        <div>
          <Link to="/dashboard" className="[&.active]:font-bold">
            Dashboard
          </Link>
        </div>
      </div>
    </>
  )
}

export default Sidebar
