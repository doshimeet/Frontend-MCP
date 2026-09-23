/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  sassOptions: {
    includePaths: ['./node_modules'],
    silenceDeprecations: ['legacy-js-api'],
  },
};

export default nextConfig;
