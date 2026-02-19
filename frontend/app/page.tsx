"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  TrendingUp,
  Zap,
  Download,
  AlertCircle,
  BarChart3,
  Play,
  Filter,
  X,
} from "lucide-react";
import ProjectsList from "@/components/ProjectsList";
import StatsCard from "@/components/StatsCard";
import Header from "@/components/Header";
import AllProjectsAnalyticsModal from "@/components/AllProjectsAnalyticsModal";
import RunDialog from "@/components/RunDialog";
import { useRealTimeMonitoring } from "@/lib/useRealTimeMonitoring";

interface Project {
  token: string;
  title: string;
  owner_email: string;
  projecturl?: string;
  main_site?: string;
  last_run: {
    status: string;
    pages: number;
    start_time: string;
    run_token: string;
  } | null;
}

interface Metadata {
  id: number;
  personal_project_id: string;
  project_name: string;
  region?: string;
  country?: string;
  brand?: string;
  website_url?: string;
  total_pages?: number;
  current_page_scraped?: number;
  last_run_date?: string;
}

interface Stats {
  total: number;
  running: number;
  completed: number;
  queued: number;
}

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [metadata, setMetadata] = useState<Metadata[]>([]);
  const [stats, setStats] = useState<Stats>({
    total: 0,
    running: 0,
    completed: 0,
    queued: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [analyticsOpen, setAnalyticsOpen] = useState(false);
  const [runDialogOpen, setRunDialogOpen] = useState(false);
  const [projectToRun, setProjectToRun] = useState<Project | null>(null);

  // Filter states
  const [regions, setRegions] = useState<string[]>([]);
  const [countries, setCountries] = useState<string[]>([]);
  const [brands, setBrands] = useState<string[]>([]);
  const [websites, setWebsites] = useState<string[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>("");
  const [selectedCountry, setSelectedCountry] = useState<string>("");
  const [selectedBrand, setSelectedBrand] = useState<string>("");
  const [selectedWebsite, setSelectedWebsite] = useState<string>("");
  const [showFilters, setShowFilters] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  // Real-time monitoring hook
  const monitoring = useRealTimeMonitoring();

  useEffect(() => {
    fetchFilters();
    fetchMetadata();
    const interval = setInterval(() => {
      fetchProjects();
      fetchMetadata();
    }, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [selectedRegion, selectedCountry, selectedBrand, selectedWebsite]);

  const fetchFilters = async () => {
    try {
      console.log("[Home] Fetching filter options...");
      
      const response = await fetch("/api/filters", {
        headers: {
          "Authorization": `Bearer ${process.env.NEXT_PUBLIC_API_KEY || 't_hmXetfMCq3'}`,
        },
      });

      if (!response.ok) {
        console.error("[Home] Filter options error:", response.status);
        return;
      }

      const data = await response.json();
      console.log("[Home] Successfully fetched filter options");
      
      if (data.filters) {
        setRegions(data.filters.regions || []);
        setCountries(data.filters.countries || []);
        setBrands(data.filters.brands || []);
        setWebsites(data.filters.websites || []);

        console.log(`[Home] Loaded filters - Regions: ${data.filters.regions?.length || 0}, Countries: ${data.filters.countries?.length || 0}, Brands: ${data.filters.brands?.length || 0}, Websites: ${data.filters.websites?.length || 0}`);
      }
    } catch (err) {
      console.error("[Home] Error fetching filter options:", err);
    }
  };

  const fetchMetadata = async () => {
    try {
      console.log("[Home] Fetching metadata...");
      
      const params = new URLSearchParams();
      const response = await fetch("/api/metadata?" + params.toString(), {
        headers: {
          "Authorization": `Bearer ${process.env.NEXT_PUBLIC_API_KEY || 't_hmXetfMCq3'}`,
        },
      });

      console.log("[Home] Metadata response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("[Home] Metadata error:", response.status, errorData);
        return;
      }

      const data = await response.json();
      console.log("[Home] Successfully fetched", data.count || 0, "metadata records");
      
      if (data.records) {
        setMetadata(data.records);
      }
    } catch (err) {
      console.error("[Home] Error fetching metadata:", err);
    }
  };

  const fetchProjects = async () => {
    try {
      setError(null);
      let url = "/api/projects";

      // Build query params from filters
      const params = new URLSearchParams();
      if (selectedRegion) params.append("region", selectedRegion);
      if (selectedCountry) params.append("country", selectedCountry);
      if (selectedBrand) params.append("brand", selectedBrand);
      if (selectedWebsite) params.append("website", selectedWebsite);

      // Use search endpoint if filters are applied, otherwise use / api/projects (which also groups)
      if (selectedRegion || selectedCountry || selectedBrand || selectedWebsite) {
        params.append("group_by_website", "true");
        url = "/api/projects/search?" + params.toString();
      }

      console.log("[Home] Fetching projects from:", url);

      const response = await fetch(url, { timeout: 300000 });
      
      console.log("[Home] Projects response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMsg = errorData.error || `HTTP ${response.status}`;
        throw new Error(`Failed to fetch projects: ${errorMsg}`);
      }

      const data = await response.json();
      console.log("[Home] Backend returned response with keys:", Object.keys(data));
      
      // Handle both grouped (by_website) and flat (projects) response formats
      let allProjects: Project[] = [];
      
      if (data.by_website && Array.isArray(data.by_website)) {
        // Grouped response format (from / api/projects or /api/projects/search with grouping)
        console.log("[Home] Processing grouped response with", data.by_website.length, "website groups");
        for (const group of data.by_website) {
          if (group.projects && Array.isArray(group.projects)) {
            allProjects.push(...group.projects);
          }
        }
      } else if (data.by_project && Array.isArray(data.by_project)) {
        // Alternative grouped format from search endpoint
        allProjects = data.by_project;
      } else if (data.projects && Array.isArray(data.projects)) {
        // Flat response format
        allProjects = data.projects;
      }
      
      console.log("[Home] Successfully fetched", allProjects.length, "total projects");
      
      if (allProjects.length > 0) {
        console.log("[Home] First 3 projects:", allProjects.slice(0, 3).map((p: Project) => p.title));
      }
      
      setProjects(allProjects);
      setLastUpdate(new Date());

      // Calculate stats
      const running =
        allProjects.filter((p: Project) => p.last_run?.status === "running").length || 0;
      const completed =
        allProjects.filter((p: Project) => p.last_run?.status === "complete").length || 0;
      const queued =
        allProjects.filter((p: Project) => p.last_run?.status === "queued").length || 0;

      setStats({
        total: allProjects.length,
        running,
        completed,
        queued,
      });

      setLoading(false);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error("[Home] Error:", errorMsg);
      setError(errorMsg);
      setLoading(false);
    }
  };

  const syncProjects = async () => {
    try {
      setSyncing(true);
      setSyncMessage(null);
      setError(null);

      console.log("[Home] Starting project sync...");

      const response = await fetch("/api/projects/sync", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${process.env.NEXT_PUBLIC_API_KEY || 't_hmXetfMCq3'}`,
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || "Failed to sync projects");
      }

      const data = await response.json();
      console.log("[Home] Sync completed:", data);

      setSyncMessage(`✅ ${data.message || `Synced ${data.total} projects to database`}`);

      // Refresh projects after sync
      setTimeout(() => {
        fetchProjects();
        setSyncing(false);
      }, 1000);

    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error("[Home] Sync error:", errorMsg);
      setError(errorMsg);
      setSyncing(false);
    }
  };

  const handleRunAll = async () => {
    try {
      setError(null);
      const response = await fetch("/api/projects/run-all", { method: "POST" });
      if (!response.ok) throw new Error("Failed to run projects");

      setTimeout(fetchProjects, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run projects");
    }
  };

  const clearFilters = () => {
    setSelectedRegion("");
    setSelectedCountry("");
    setSelectedBrand("");
    setSelectedWebsite("");
  };

  const hasActiveFilters = selectedRegion || selectedCountry || selectedBrand || selectedWebsite;

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Header />

      {/* Error Alert */}
      {error && (
        <div className="container mx-auto px-6 py-4 mt-6">
          <div className="bg-red-900/30 backdrop-blur-sm border border-red-700/50 rounded-xl p-4 flex items-start gap-3 shadow-lg shadow-red-900/20">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-300">Error</p>
              <p className="text-red-400 text-sm mt-0.5">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Success Message */}
      {syncMessage && (
        <div className="container mx-auto px-6 py-4 mt-6">
          <div className="bg-green-900/30 backdrop-blur-sm border border-green-700/50 rounded-xl p-4 flex items-start gap-3 shadow-lg shadow-green-900/20">
            <div className="text-green-400 flex-shrink-0 mt-0.5">✅</div>
            <div>
              <p className="font-semibold text-green-300">Success</p>
              <p className="text-green-400 text-sm mt-0.5">{syncMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Stats Section */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-8">
          <StatsCard
            title="Total Projects"
            value={stats.total}
            icon={<TrendingUp className="w-6 h-6" />}
            color="bg-blue-500"
          />
          <StatsCard
            title="Running"
            value={stats.running}
            icon={<Activity className="w-6 h-6" />}
            color="bg-green-500"
          />
          <StatsCard
            title="Queued"
            value={stats.queued}
            icon={<Zap className="w-6 h-6" />}
            color="bg-yellow-500"
          />
          <StatsCard
            title="Completed"
            value={stats.completed}
            icon={<Download className="w-6 h-6" />}
            color="bg-purple-500"
          />
        </div>

        {/* Action Buttons */}
        <div className="mb-8 flex gap-4 flex-wrap items-center">
          <button
            onClick={syncProjects}
            disabled={syncing || loading}
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-700 hover:to-cyan-800 disabled:from-slate-700 disabled:to-slate-700 rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-cyan-500/25 disabled:shadow-none transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
          >
            <Download className={`w-5 h-5 ${syncing ? "animate-spin" : ""}`} />
            {syncing ? "Syncing..." : "Sync Projects"}
          </button>
          <button
            onClick={handleRunAll}
            disabled={loading}
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-slate-700 disabled:to-slate-700 rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-blue-500/25 disabled:shadow-none transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
          >
            <Play className="w-5 h-5" />
            Run All Projects
          </button>
          <button
            onClick={() => setAnalyticsOpen(true)}
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-purple-500/25 transform hover:scale-105"
          >
            <BarChart3 className="w-5 h-5" />
            Analytics
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-semibold transition-all duration-200 border ${
              hasActiveFilters
                ? "bg-amber-900/30 border-amber-600/50 text-amber-300"
                : "bg-slate-800 hover:bg-slate-700 border-slate-700"
            }`}
          >
            <Filter className="w-5 h-5" />
            Filters {hasActiveFilters && "✓"}
          </button>
          <button
            onClick={fetchProjects}
            disabled={loading}
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800/50 border border-slate-700 hover:border-slate-600 rounded-xl font-semibold transition-all duration-200 disabled:cursor-not-allowed"
          >
            <Activity className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
          {lastUpdate && (
            <div className="ml-auto flex items-center gap-2 px-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-xl">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
              <span className="text-slate-400 text-sm font-medium">
                Updated {lastUpdate.toLocaleTimeString()}
              </span>
            </div>
          )}
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mb-8 p-6 bg-slate-800/50 border border-slate-700/50 rounded-xl backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-200">Filters</h3>
              <button
                onClick={() => setShowFilters(false)}
                className="p-1 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Region</label>
                <select
                  value={selectedRegion}
                  onChange={(e) => setSelectedRegion(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="">All Regions</option>
                  {regions.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Country</label>
                <select
                  value={selectedCountry}
                  onChange={(e) => setSelectedCountry(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="">All Countries</option>
                  {countries.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Brand</label>
                <select
                  value={selectedBrand}
                  onChange={(e) => setSelectedBrand(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="">All Brands</option>
                  {brands.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Website</label>
                <select
                  value={selectedWebsite}
                  onChange={(e) => setSelectedWebsite(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="">All Websites</option>
                  {websites.map((w) => (
                    <option key={w} value={w}>
                      {w}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-slate-300 transition-colors"
              >
                Clear Filters
              </button>
            )}
          </div>
        )}

        {/* Projects List */}
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-flex flex-col items-center gap-6">
              <div className="relative">
                <div className="animate-spin rounded-full h-16 w-16 border-4 border-slate-700 border-t-blue-500"></div>
                <div className="absolute inset-0 rounded-full bg-blue-500/20 animate-pulse"></div>
              </div>
              <div>
                <p className="text-slate-300 text-lg font-semibold">
                  Loading projects...
                </p>
                <p className="text-slate-500 text-sm mt-1">
                  Please wait while we fetch your data
                </p>
              </div>
            </div>
          </div>
        ) : (
          <ProjectsList
            projects={projects}
            onRunProject={async (token: string) => {
              const project = projects.find((p) => p.token === token);
              if (project) {
                setProjectToRun(project);
                setRunDialogOpen(true);
              }
            }}
          />
        )}
      </section>

      {/* Run Dialog */}
      {projectToRun && (
        <RunDialog
          isOpen={runDialogOpen}
          onClose={() => setRunDialogOpen(false)}
          projectToken={projectToRun.token}
          projectTitle={projectToRun.title}
          projectURL={projectToRun.projecturl || projectToRun.main_site || ""}
          onRunStart={async (runToken: string, pages: number) => {
            // Start real-time monitoring
            try {
              await monitoring.startMonitoring(
                projectToRun.token,
                runToken,
                pages,
              );
            } catch (err) {
              console.error("Failed to start monitoring:", err);
            }

            await fetchProjects();
            // Show analytics modal for all projects
            setAnalyticsOpen(true);
          }}
        />
      )}

      {/* Analytics Modal */}
      <AllProjectsAnalyticsModal
        isOpen={analyticsOpen}
        onClose={() => {
          setAnalyticsOpen(false);
        }}
        projects={projects}
      />
    </main>
  );
}
