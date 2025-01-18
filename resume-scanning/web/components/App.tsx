import { Box } from "@bigcommerce/big-design";
import { Provider as GadgetProvider } from "@gadgetinc/react-bigcommerce";
import { RouterProvider, createBrowserRouter } from "react-router";
import { api } from "../api";
import ScanningInterface from "./ScanningInterface";

 
export const router = createBrowserRouter([
  {
    path: "/",
    element: <Box
      marginHorizontal={{ mobile: 'none', tablet: 'xxxLarge' }}
      marginVertical={{ mobile: 'none', tablet: "xxLarge" }}
    >
      <ScanningInterface />
    </Box>
  }
]);

 
export default function App() {
  return (
    <GadgetProvider api={api}>
      <RouterProvider router={router} />
    </GadgetProvider>
  );
}
