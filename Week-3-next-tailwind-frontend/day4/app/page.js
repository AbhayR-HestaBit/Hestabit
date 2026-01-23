mport Image from "next/image";

export const metadata = {
  title: "Dashboard – Next.js",
  description:
    "A modern dashboard built with Next.js App Router and Tailwind CSS.",
};

export default function HomePage() {
  return (
    <main className="space-y-24">
     //hero-section
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <div className="space-y-6">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-100">
            Building dashboards
          </h1>
          <p className="text-gray-600 text-lg">
            A clean, scalable admin dashboard built using
            Next.js App Router and Tailwind CSS.
          </p>
          <div className="flex gap-4">
            <button className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-300">
              Get Started
            </button>
            <button className="px-6 py-3 border rounded hover:bg-gray-500">
              View Demo
            </button>
          </div>
        </div>
	//image-dashboard
        <div className="relative w-full h-[300px] lg:h-[400px]">
          <Image
            src="/dashboard-preview.png"
            alt="Dashboard preview"
            fill
            className="object-contain"
            priority
          />
        </div>
     </section>
    </main>
  );
}
