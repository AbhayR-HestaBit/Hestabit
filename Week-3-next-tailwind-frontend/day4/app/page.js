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
//feature-section
<section className="grid grid-cols-1 md:grid-cols-3 gap-8">
  {[
    {
      title: "Fast Development",
      desc: "Build scalable dashboards quickly using reusable components.",
    },
    {
      title: "Modern Stack",
      desc: "Next.js App Router with Tailwind CSS for rapid UI development.",
    },
    {
      title: "Responsive Design",
      desc: "Fully responsive layouts that work across all devices.",
    },
  ].map((item) => (
    <div
      key={item.title}
      className="p-6 border rounded text-center space-y-2"
    >
      <h3 className="font-semibold text-gray-200">
        {item.title}
      </h3>
      <p className="text-sm text-gray-400">
        {item.desc}
      </p>
    </div>
  ))}
</section>
//Testimonials
<section className="bg-gray-900 rounded p-12 space-y-8">
  <h2 className="text-2xl font-semibold text-center text-gray-200">
    What Users Say
  </h2>

  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
    <div className="bg-white p-6 rounded shadow-sm">
      <p className="text-gray-600">
        “This dashboard structure saved me weeks of setup time.”
      </p>
      <p className="mt-4 text-sm font-semibold text-gray-900">
        — Anonymous User
      </p>
    </div>

    <div className="bg-white p-6 rounded shadow-sm">
      <p className="text-gray-600">
        “Clean architecture and perfect for real-world apps.”
      </p>
      <p className="mt-4 text-sm font-semibold text-gray-900">
        — Anonymous User
      </p>
    </div>
  </div>
</section>
//footer
<footer className="border-t pt-8 text-center text-sm text-gray-500">
  © {new Date().getFullYear()} Dashboard. All rights reserved.
</footer>
    </main>
  );
}
