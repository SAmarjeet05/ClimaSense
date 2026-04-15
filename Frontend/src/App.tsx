import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthContext, useAuthProvider } from "@/hooks/useAuth";
import { ProtectedRoute, AdminRoute } from "@/components/layout/ProtectedRoute";
import { MainLayout } from "@/components/layout/MainLayout";
import Login from "@/pages/Login";
import Dashboard from "@/pages/user/Dashboard";
import InsightsComparison from "@/pages/user/InsightsComparison";
import ClimateMap from "@/pages/user/ClimateMap";
import ForecastSimulator from "@/pages/user/ForecastSimulator";
import Assistant from "@/pages/user/Assistant";
import AdminOverview from "@/pages/admin/AdminOverview";
import DatasetManagement from "@/pages/admin/DatasetManagement";
import ModelManagement from "@/pages/admin/ModelManagement";
import UserManagement from "@/pages/admin/UserManagement";
import SystemLogs from "@/pages/admin/SystemLogs";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const AppRoutes = () => {
  const auth = useAuthProvider();

  return (
    <AuthContext.Provider value={auth}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/insights" element={<InsightsComparison />} />
            <Route path="/insights-comparison" element={<InsightsComparison />} />
            <Route path="/climate-map" element={<ClimateMap />} />
            <Route path="/map" element={<ClimateMap />} />
            <Route path="/forecast" element={<ForecastSimulator />} />
            <Route path="/assistant" element={<Assistant />} />
            <Route element={<AdminRoute />}>
              <Route path="/admin" element={<AdminOverview />} />
              <Route path="/admin/datasets" element={<DatasetManagement />} />
              <Route path="/admin/models" element={<ModelManagement />} />
              <Route path="/admin/users" element={<UserManagement />} />
              <Route path="/admin/logs" element={<SystemLogs />} />
            </Route>
          </Route>
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthContext.Provider>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
