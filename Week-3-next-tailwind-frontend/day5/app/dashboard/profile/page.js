import Image from "next/image";
import Link from "next/link";

export default function ProfilePage() {
  return (
    <div className="space-y-6">
      <Link
        href="/dashboard"
        className="text-sm text-blue-600 hover:underline"
      >
        Go back
      </Link>

      <div className="bg-bg-zinc-700 rounded shadow-sm p-6 space-y-6">

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">

          <div className="flex justify-center md:justify-start">
            <div className="relative w-32 h-32 rounded overflow-hidden">
              <Image
                src="/profile.png"
                alt="Profile picture"
                fill
                className="object-cover"
                priority
              />
            </div>
          </div>

          <div className="md:col-span-1 space-y-3 text-sm">
            <div>
              <p className="text-gray-300">Name</p>
              <p className="font-medium text-gray-200">
                Nina Valentine
              </p>
            </div>

            <div>
              <p className="text-gray-300">Job Title</p>
              <p className="font-medium text-gray-200">
                Actress
              </p>
            </div>

            <div>
              <p className="text-gray-300">Email</p>
              <a
                href="mailto:nina_val@example.com"
                className="text-blue-500 hover:underline"
              >
                nina_val@example.com
              </a>
            </div>
          </div>

          <div className="space-y-3 text-sm">
            <div>
              <p className="text-gray-300">LinkedIn</p>
              <a
                href="#"
                className="text-blue-500 hover:underline"
              >
                linkedin.com
              </a>
            </div>

            <div>
              <p className="text-gray-300">Twitter</p>
              <a
                href="#"
                className="text-blue-600 hover:underline"
              >
                x.com
              </a>
            </div>

            <div>
              <p className="text-gray-300">Facebook</p>
              <a
                href="#"
                className="text-blue-600 hover:underline"
              >
                facebook.com
              </a>
            </div>
          </div>
        </div>

        <div className="border-t pt-4">
          <p className="text-gray-500 text-sm mb-1">
            Bio
          </p>
          <p className="text-gray-300 text-sm leading-relaxed">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            Praesent aliquet odio augue, in dapibus lacus imperdiet ut.
            Quisque elementum placerat neque rhoncus tempus.
            Cras id suscipit diam, sit amet rutrum ipsum.
            Vestibulum rutrum elit lacinia sapien porta pulvinar.
          </p>
        </div>

        <div>
          <button className="text-sm text-blue-600 hover:underline">
            Edit Profile
          </button>
        </div>
      </div>
    </div>
  );
}

