/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    webpackDevMiddleware: config => {
        config.watchOptions = {
            poll: 1000,
            aggregateTimeout: 300,
        };
        return config;
    },
    async rewrites() {
        return [
            {
                source: '/be/:path*',
                destination: `${process.env.NEXT_PUBLIC_BACKEND}/be/:path*`,
            },
            {
                source: '/ums/:path*',
                destination: `${process.env.NEXT_PUBLIC_UMS}/ums/:path*`,
            },
            {
                source: '/healthz',
                destination: '/api/health',
            },
            {
                source: '/resr/:path*',
                destination: 'https://resr.dreamy.kr/:path*',
            },
        ];
    },
};

module.exports = nextConfig;
