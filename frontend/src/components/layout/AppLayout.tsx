import { AnimatePresence, motion } from "framer-motion";
import { Navigate, useLocation, useOutlet } from "react-router-dom";

import AdBanner from "@/components/ui/AdBanner";
import AnimatedBackground from "@/components/ui/AnimatedBackground";
import BottomNav from "@/components/layout/BottomNav";
import { useAuthStore } from "@/store/authStore";

export default function AppLayout() {
  const accessToken = useAuthStore((state) => state.accessToken);
  const location = useLocation();
  const element = useOutlet();

  if (!accessToken) {
    return <Navigate to="/connexion" replace />;
  }

  return (
    <div className="min-h-screen pb-24">
      <AnimatedBackground variant="light" />
      <div className="relative z-10 pt-2">
        <AdBanner />
      </div>
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.18 }}
        >
          {element}
        </motion.div>
      </AnimatePresence>
      <BottomNav />
    </div>
  );
}
