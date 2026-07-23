import { useEffect, useState } from "react";

import ErrorMessage from "@/components/ui/ErrorMessage";
import Loader from "@/components/ui/Loader";
import { getErrorMessage } from "@/lib/errors";
import { searchProfiles } from "@/services/endpoints/auth";
import {
  acceptFriendRequest,
  declineFriendRequest,
  listFriendRequests,
  listFriends,
  sendFriendRequest,
} from "@/services/endpoints/social";
import { useProfileStore } from "@/store/profileStore";
import type { Friend, UserProfile } from "@/types/api";

type Tab = "friends" | "requests" | "search";

export default function FriendsPage() {
  const { profile, refresh: refreshProfile } = useProfileStore();
  const [tab, setTab] = useState<Tab>("friends");
  const [friends, setFriends] = useState<UserProfile[]>([]);
  const [requests, setRequests] = useState<Friend[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<UserProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [friendList, requestList] = await Promise.all([
        listFriends(),
        listFriendRequests(),
        profile ? Promise.resolve(profile) : refreshProfile(),
      ]);
      setFriends(friendList);
      setRequests(requestList);
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de charger tes amis."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSearch(event: React.FormEvent) {
    event.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      setSearchResults(await searchProfiles(searchQuery.trim()));
    } catch (err) {
      setFeedback(getErrorMessage(err, "Recherche impossible."));
    }
  }

  async function handleAdd(addresseeId: string) {
    try {
      await sendFriendRequest(addresseeId);
      setFeedback("Demande envoyee !");
      setSearchResults((prev) => prev.filter((p) => p.id !== addresseeId));
    } catch (err) {
      setFeedback(getErrorMessage(err, "Impossible d'envoyer la demande."));
    }
  }

  async function handleAccept(id: string) {
    await acceptFriendRequest(id);
    await load();
  }

  async function handleDecline(id: string) {
    await declineFriendRequest(id);
    await load();
  }

  const incomingRequests = requests.filter((r) => r.status === "pending" && r.addressee.id === profile?.id);

  return (
    <section className="min-h-screen p-4">
      <div className="mb-4 flex items-center gap-3">
        <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-haiti-blue text-2xl shadow-card">
          🤝
        </span>
        <h1 className="font-display text-2xl text-haiti-blue">Amis</h1>
      </div>

      <div className="mb-4 flex gap-2">
        {(
          [
            ["friends", "Mes amis"],
            ["requests", `Demandes (${incomingRequests.length})`],
            ["search", "Rechercher"],
          ] as [Tab, string][]
        ).map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => setTab(value)}
            className={`rounded-pill border-2 px-3 py-1.5 text-sm font-display transition-all duration-150 ${
              tab === value
                ? "border-haiti-blue bg-haiti-blue text-white"
                : "border-slate-100 bg-white text-haiti-blue"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {feedback && <p className="mb-3 text-sm text-haiti-green">{feedback}</p>}

      {isLoading ? (
        <Loader />
      ) : error ? (
        <ErrorMessage message={error} onRetry={load} />
      ) : (
        <>
          {tab === "friends" && (
            <div className="space-y-2">
              {friends.length === 0 && <p className="text-slate-500">Aucun ami pour le moment.</p>}
              {friends.map((friend) => (
                <div key={friend.id} className="card-game flex items-center justify-between py-3">
                  <span className="flex items-center gap-2">
                    <span className="flex h-9 w-9 items-center justify-center rounded-full bg-haiti-blueLight font-display text-haiti-blue">
                      {friend.user.username.charAt(0).toUpperCase()}
                    </span>
                    {friend.user.username}
                  </span>
                  <span className="rounded-pill bg-slate-100 px-2 py-1 text-sm text-slate-500">
                    Niveau {friend.level}
                  </span>
                </div>
              ))}
            </div>
          )}

          {tab === "requests" && (
            <div className="space-y-2">
              {incomingRequests.length === 0 && <p className="text-slate-500">Aucune demande en attente.</p>}
              {incomingRequests.map((request) => (
                <div key={request.id} className="card-game flex items-center justify-between py-3">
                  <span className="flex items-center gap-2">
                    <span className="flex h-9 w-9 items-center justify-center rounded-full bg-haiti-blueLight font-display text-haiti-blue">
                      {request.requester.user.username.charAt(0).toUpperCase()}
                    </span>
                    {request.requester.user.username}
                  </span>
                  <div className="flex gap-2">
                    <button type="button" onClick={() => handleAccept(request.id)} className="btn-game-primary px-3 py-1 text-sm">
                      Accepter
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDecline(request.id)}
                      className="btn-game-secondary px-3 py-1 text-sm"
                    >
                      Refuser
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {tab === "search" && (
            <div>
              <form onSubmit={handleSearch} className="mb-3 flex gap-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Nom d'utilisateur"
                  className="flex-1 rounded-pill border border-slate-200 px-4 py-2 outline-none focus:border-haiti-blue"
                />
                <button type="submit" className="btn-game-secondary px-4 text-sm">
                  Chercher
                </button>
              </form>
              <div className="space-y-2">
                {searchResults
                  .filter((p) => p.id !== profile?.id)
                  .map((result) => (
                    <div key={result.id} className="card-game flex items-center justify-between py-3">
                      <span className="flex items-center gap-2">
                        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-haiti-blueLight font-display text-haiti-blue">
                          {result.user.username.charAt(0).toUpperCase()}
                        </span>
                        {result.user.username}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleAdd(result.id)}
                        className="btn-game-primary px-3 py-1 text-sm"
                      >
                        Ajouter
                      </button>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
