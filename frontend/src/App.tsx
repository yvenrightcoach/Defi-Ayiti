import { Navigate, Route, Routes } from "react-router-dom";

import { useGlobalClickSound } from "@/hooks/useGlobalClickSound";
import AppLayout from "@/components/layout/AppLayout";
import AdventureMapPage from "@/pages/AdventureMapPage";
import BattlePage from "@/pages/BattlePage";
import DepartmentDetailPage from "@/pages/DepartmentDetailPage";
import FriendsPage from "@/pages/FriendsPage";
import HeroesPage from "@/pages/HeroesPage";
import HomePage from "@/pages/HomePage";
import LeaderboardPage from "@/pages/LeaderboardPage";
import LoginPage from "@/pages/LoginPage";
import ProfilePage from "@/pages/ProfilePage";
import QuizPage from "@/pages/QuizPage";

export default function App() {
  useGlobalClickSound();

  return (
    <Routes>
      <Route path="/connexion" element={<LoginPage />} />

      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/aventure" element={<AdventureMapPage />} />
        <Route path="/aventure/:departmentId" element={<DepartmentDetailPage />} />
        <Route path="/quiz" element={<QuizPage />} />
        <Route path="/quiz/level/:levelId" element={<QuizPage />} />
        <Route path="/battle" element={<BattlePage />} />
        <Route path="/heros" element={<HeroesPage />} />
        <Route path="/amis" element={<FriendsPage />} />
        <Route path="/classements" element={<LeaderboardPage />} />
        <Route path="/profil" element={<ProfilePage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
