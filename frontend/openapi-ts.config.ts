import { defaultPlugins, defineConfig } from "@hey-api/openapi-ts"

export default defineConfig({
  input: "./openapi.json",
  output: {
    lint: false,
    path: "./src/client",
  },
  plugins: [
    {
      name: "@hey-api/client-axios",
      throwOnError: true,
    },
    "@tanstack/react-query",
    "@hey-api/typescript",
    {
      name: "@hey-api/sdk",
      // NOTE: this doesn't allow tree-shaking
      asClass: true,
    },
  ],
})
