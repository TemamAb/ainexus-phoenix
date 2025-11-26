#!/bin/bash

# ==========================================
# QUANTUMNEX: GRAFANA AUTONOMY ENGINE BUILDER
# ==========================================

echo ">> [INIT] DETECTING ENVIRONMENT..."
echo ">> [INIT] CONSTRUCTING QUANTUMNEX ONE-CLICK FORTRESS..."

# 1. SCAFFOLD PROJECT
npx create-next-app@latest quantumnex-grafana \
  --typescript --tailwind --eslint --app --no-src-dir --import-alias "@/*" --use-npm

cd quantumnex-grafana

# 2. INSTALL VISUALIZATION & LOGIC DEPS
echo ">> [DEPS] INSTALLING RECHARTS, LUCIDE, & LOGIC CORES..."
npm install recharts lucide-react clsx tailwind-merge framer-motion ethers @web3modal/ethers
