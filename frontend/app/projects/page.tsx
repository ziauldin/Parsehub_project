"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  Filter,
  X,
  Play,
  PlayCircle,
  Clock,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import Header from "@/components/Header";

interface Metadata {
  id: number;
  personal_project_id: string;
  project_token?: string;
  project_name: string;
  region?: string;
  country?: string;
  brand?: string;
  website_url?: string;
  total_pages?: number;
  total_products?: number;
  current_page_scraped?: number;
  current_product_scraped?: number;
  last_run_date?: string;
  updated_date?: string;
}

interface ExecutionQueue {
  metadata_id: number;
  project_name: string;
  status: "pending" | "running" | "completed" | "failed";
  progress?: number;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Metadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [regions, setRegions] = useState<string[]>([]);
  const [countries, setCountries] = useState<string[]>([]);
  const [brands, setBrands] = useState<string[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>("");
  const [selectedCountry, setSelectedCountry] = useState<string>("");
  const [selectedBrand, setSelectedBrand] = useState<string>("");
  const [showFilters, setShowFilters] = useState(false);

  // Selection and execution states
  const [selectedProjects, setSelectedProjects] = useState<Set<number>>(new Set());
  const [executionQueue, setExecutionQueue] = useState<ExecutionQueue[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);

  // Sorting states
  const [sortBy, setSortBy] = useState<"name" | "date" | "progress">("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    fetchProjects();
    const interval = setInterval(fetchProjects, 30000);
    return () => clearInterval(interval);
  }, [selectedRegion, selectedCountry, selectedBrand]);

  const fetchProjects = async () => {
    try {
      setError(null);
      const params = new URLSearchParams();
      if (selectedRegion) params.append("region", selectedRegion);
      if (selectedCountry) params.append("country", selectedCountry);
      if (selectedBrand) params.append("brand", selectedBrand);

      const url = "/api/metadata?" + params.toString();
      console.log("[Projects] Fetching metadata from:", url);

      const response = await fetch(url, {
        headers: {
          "Authorization": `Bearer ${process.env.NEXT_PUBLIC_API_KEY || 't_hmXetfMCq3'}`,
        },
      });

      console.log("[Projects] Response status:", response.status, response.statusText);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMsg = errorData.error || errorData.details || `HTTP ${response.status} ${response.statusText}`;
        console.error("[Projects] API Error:", errorMsg, errorData);
        throw new Error(`Failed to fetch projects: ${errorMsg}`);
      }

      const data = await response.json();
      console.log("[Projects] Successfully fetched", data.count || 0, "records");

      if (data.records && Array.isArray(data.records)) {
        setProjects(data.records);

        // Extract unique values for filters
        const regionSet = new Set(data.records.map((r: Metadata) => r.region).filter(Boolean));
        const countrySet = new Set(data.records.map((r: Metadata) => r.country).filter(Boolean));
        const brandSet = new Set(data.records.map((r: Metadata) => r.brand).filter(Boolean));

        setRegions(Array.from(regionSet) as string[]);
        setCountries(Array.from(countrySet) as string[]);
        setBrands(Array.from(brandSet) as string[]);

        console.log(`[Projects] Loaded filters - Regions: ${regionSet.size}, Countries: ${countrySet.size}, Brands: ${brandSet.size}`);
      } else {
        console.warn("[Projects] No records array in response:", data);
        setProjects([]);
      }

      setLoading(false);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error("[Projects] Error:", errorMsg);
      setError(errorMsg);
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setSelectedRegion("");
    setSelectedCountry("");
    setSelectedBrand("");
  };

  const hasActiveFilters = selectedRegion || selectedCountry || selectedBrand;

  const toggleProjectSelection = (id: number) => {
    const newSelected = new Set(selectedProjects);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedProjects(newSelected);
  };

  const toggleAllSelection = () => {
    if (selectedProjects.size === projects.length) {
      setSelectedProjects(new Set());
    } else {
      setSelectedProjects(new Set(projects.map((p) => p.id)));
    }
  };

  const handleRunSelected = async () => {
    if (selectedProjects.size === 0) return;

    setIsExecuting(true);
    const queue: ExecutionQueue[] = Array.from(selectedProjects).map((id) => {
      const project = projects.find((p) => p.id === id)!;
      return {
        metadata_id: id,
        project_name: project.project_name,
        status: "pending" as const,
        progress: 0,
      };
    });

    setExecutionQueue(queue);

    try {
      console.log("[Projects] Starting batch execution for", queue.length, "projects");
      
      const response = await fetch("/api/runs/batch-execute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${process.env.NEXT_PUBLIC_API_KEY || 't_hmXetfMCq3'}`,
        },
        body: JSON.stringify({
          metadata_ids: Array.from(selectedProjects),
        }),
      });

      console.log("[Projects] Batch execute response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMsg = errorData.error || `HTTP ${response.status}`;
        console.error("[Projects] Batch execution error:", errorMsg);
        throw new Error(`Failed to queue batch execution: ${errorMsg}`);
      }

      const data = await response.json();
      console.log("[Projects] Batch execution queued successfully");

      // Simulate execution progress (real implementation would poll backend)
      for (let i = 0; i < queue.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        setExecutionQueue((prev) => {
          const updated = [...prev];
          updated[i] = { ...updated[i], status: "running" as const };
          return updated;
        });

        await new Promise((resolve) => setTimeout(resolve, 5000));
        setExecutionQueue((prev) => {
          const updated = [...prev];
          updated[i] = { ...updated[i], status: "completed" as const, progress: 100 };
          return updated;
        });
      }

      setSelectedProjects(new Set());
      console.log("[Projects] Batch execution completed");
      await fetchProjects();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error("[Projects] Batch execution failed:", errorMsg);
      setError(errorMsg);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleRunAll = async () => {
    setSelectedProjects(new Set(projects.map((p) => p.id)));
    // Will trigger batch execution on next button click
    handleRunSelected();
  };

  const sortedProjects = [...projects].sort((a, b) => {
    let compareValue = 0;

    if (sortBy === "name") {
      compareValue = a.project_name.localeCompare(b.project_name);
    } else if (sortBy === "date") {
      const dateA = new Date(a.last_run_date || a.updated_date || 0).getTime();
      const dateB = new Date(b.last_run_date || b.updated_date || 0).getTime();
      compareValue = dateA - dateB;
    } else if (sortBy === "progress") {
      const progressA = (a.current_page_scraped || 0) / (a.total_pages || 1);
      const progressB = (b.current_page_scraped || 0) / (b.total_pages || 1);
      compareValue = progressA - progressB;
    }

    return sortOrder === "asc" ? compareValue : -compareValue;
  });

  const getProgressPercentage = (project: Metadata) => {
    if (!project.total_pages || project.total_pages <= 0) return 0;
    return Math.min(100, (project.current_page_scraped || 0 / project.total_pages) * 100);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Header />

      <section className="container mx-auto px-6 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-900/30 backdrop-blur-sm border border-red-700/50 rounded-xl p-4 flex items-start gap-3 shadow-lg shadow-red-900/20">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-300">Error</p>
              <p className="text-red-400 text-sm mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Title and controls */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">Projects Management</h1>
            <p className="text-slate-400">Manage and execute your scraping projects</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all duration-200 border ${
                hasActiveFilters
                  ? "bg-amber-900/30 border-amber-600/50 text-amber-300"
                  : "bg-slate-800 hover:bg-slate-700 border-slate-700"
              }`}
            >
              <Filter className="w-4 h-4" />
              Filters {hasActiveFilters && "✓"}
            </button>
          </div>
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
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
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

        {/* Action Bar */}
        <div className="mb-6 flex gap-3 items-center flex-wrap">
          <div className="text-sm text-slate-400">
            {selectedProjects.size > 0
              ? `${selectedProjects.size} project${selectedProjects.size !== 1 ? "s" : ""} selected`
              : "Select projects to run"}
          </div>
          <button
            onClick={handleRunSelected}
            disabled={selectedProjects.size === 0 || isExecuting}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 rounded-lg font-medium text-white disabled:text-slate-500 transition-all duration-200 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4" />
            Run Selected
          </button>
          <button
            onClick={handleRunAll}
            disabled={projects.length === 0 || isExecuting}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 rounded-lg font-medium text-white disabled:text-slate-500 transition-all duration-200 disabled:cursor-not-allowed"
          >
            <PlayCircle className="w-4 h-4" />
            Run All Filtered
          </button>
        </div>

        {/* Execution Queue Status */}
        {executionQueue.length > 0 && (
          <div className="mb-8 p-6 bg-slate-800/50 border border-slate-700/50 rounded-xl backdrop-blur-sm">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Execution Queue</h3>
            <div className="space-y-3">
              {executionQueue.map((item) => (
                <div
                  key={item.metadata_id}
                  className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg border border-slate-600/50"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {item.status === "running" && (
                      <Activity className="w-5 h-5 text-blue-400 animate-spin" />
                    )}
                    {item.status === "completed" && (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    )}
                    {item.status === "pending" && (
                      <Clock className="w-5 h-5 text-yellow-400" />
                    )}
                    {item.status === "failed" && (
                      <AlertCircle className="w-5 h-5 text-red-400" />
                    )}
                    <div>
                      <p className="text-slate-200 font-medium">{item.project_name}</p>
                      <p className="text-slate-400 text-sm capitalize">{item.status}</p>
                    </div>
                  </div>
                  {item.progress !== undefined && (
                    <div className="w-20 h-2 bg-slate-600 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 transition-all duration-300"
                        style={{ width: `${item.progress}%` }}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Projects Table */}
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-flex flex-col items-center gap-6">
              <div className="relative">
                <div className="animate-spin rounded-full h-16 w-16 border-4 border-slate-700 border-t-blue-500"></div>
              </div>
              <p className="text-slate-300 text-lg font-semibold">Loading projects...</p>
            </div>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-20 bg-slate-800/30 border border-slate-700/50 rounded-xl">
            <p className="text-slate-400 text-lg">No projects found</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-slate-700/50 bg-slate-800/30 backdrop-blur-sm">
            <table className="w-full">
              <thead className="bg-slate-800/60 border-b border-slate-700/50">
                <tr>
                  <th className="px-6 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedProjects.size === projects.length && projects.length > 0}
                      onChange={toggleAllSelection}
                      className="w-4 h-4 rounded border-slate-600 bg-slate-700 text-blue-600"
                    />
                  </th>
                  <th
                    className="px-6 py-3 text-left text-sm font-semibold text-slate-300 cursor-pointer hover:text-slate-100"
                    onClick={() => {
                      if (sortBy === "name") {
                        setSortOrder(sortOrder === "asc" ? "desc" : "asc");
                      } else {
                        setSortBy("name");
                        setSortOrder("asc");
                      }
                    }}
                  >
                    Project Name {sortBy === "name" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Website</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Brand</th>
                  <th className="px-6 py-3 text-center text-sm font-semibold text-slate-300">Total Pages</th>
                  <th className="px-6 py-3 text-center text-sm font-semibold text-slate-300">Scraped Pages</th>
                  <th className="px-6 py-3 text-center text-sm font-semibold text-slate-300">Progress</th>
                  <th
                    className="px-6 py-3 text-left text-sm font-semibold text-slate-300 cursor-pointer hover:text-slate-100"
                    onClick={() => {
                      if (sortBy === "date") {
                        setSortOrder(sortOrder === "asc" ? "desc" : "asc");
                      } else {
                        setSortBy("date");
                        setSortOrder("desc");
                      }
                    }}
                  >
                    Last Run {sortBy === "date" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {sortedProjects.map((project) => {
                  const progress = getProgressPercentage(project);
                  return (
                    <tr
                      key={project.id}
                      className="hover:bg-slate-700/30 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedProjects.has(project.id)}
                          onChange={() => toggleProjectSelection(project.id)}
                          className="w-4 h-4 rounded border-slate-600 bg-slate-700 text-blue-600"
                        />
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-200 font-medium">{project.project_name}</td>
                      <td className="px-6 py-4 text-sm text-slate-400">{project.website_url || "—"}</td>
                      <td className="px-6 py-4 text-sm text-slate-400">{project.brand || "—"}</td>
                      <td className="px-6 py-4 text-sm text-center text-slate-300">{project.total_pages || "—"}</td>
                      <td className="px-6 py-4 text-sm text-center text-slate-300">{project.current_page_scraped || 0}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-slate-600 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                          <span className="text-xs text-slate-400 w-8 text-right">{Math.round(progress)}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-400">
                        {project.last_run_date
                          ? new Date(project.last_run_date).toLocaleDateString()
                          : "Never"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
