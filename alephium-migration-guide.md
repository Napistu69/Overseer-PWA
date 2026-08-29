# Alephium 2.0 Migration Guide
## Compendium Oracle System

## Phase 1: Setup & Wallet (Week 1)

### 1.1 Download Wallet
- [ ] Visit https://wallet.alephium.org/
- [ ] Select "Create New Wallet"
- [ ] Choose "Testnet" network
- [ ] **CRITICAL:** Write down recovery phrase on paper
- [ ] Set strong password
- [ ] Store recovery phrase offline

### 1.2 Get Testnet Tokens
- [ ] Visit https://faucet.alephium.org/
- [ ] Connect your new wallet
- [ ] Request testnet tokens (AT)
- [ ] Verify balance in wallet

### 1.3 Network Configuration
- [ ] Testnet RPC: `https://testnet.alephium.org/`
- [ ] Mainnet RPC: `https://mainnet.alephium.org/`
- [ ] Testnet explorer: `https://testnet.alephium.org/`

---

## Phase 2: Smart Contract Development (Week 2-3)

### 2.1 Development Environment
- [ ] Install Node.js (v18+)
- [ ] Install Rust (for Alephium tooling)
- [ ] Install Alephium CLI: `npm install -g @alephium/alephium-cli`
- [ ] Set up VS Code with Solidity/TypeScript extension

### 2.2 Contract Architecture
- [ ] Oracle Content Contract (verification)
- [ ] Contributor Reward Contract
- [ ] Chain-of-Custody Contract
- [ ] Treasury Management Contract

### 2.3 Development Resources
- [ ] Alephium 2.0 Docs: https://docs.alephium.org/smart-contracts/
- [ ] GitHub: https://github.com/alephium
- [ ] Discord: https://discord.gg/alephium

---

## Phase 3: Oracle Contracts (Week 4-6)

### 3.1 Content Verification Contract
**Purpose:** Verify Compendium chapters are authentic

**Functions:**
- `submitChapter(content, author, timestamp)` - Submit new content
- `verifyChapter(chapterId, authorAddress)` - Verify authenticity
- `getChapterStatus(chapterId)` - Check verification status

### 3.2 Contributor Reward Contract
**Purpose:** Reward those who add to the Oracle

**Functions:**
- `contribute(content, hash)` - Submit contribution
- `claimReward(contributionId)` - Claim token reward
- `verifyContribution(contributionId)` - Admin verification

### 3.3 Chain-of-Custody Contract
**Purpose:** Track content provenance

**Functions:**
- `registerContent(content, author, timestamp)` - Initial registration
- `transferOwnership(contentId, newAuthor)` - Transfer rights
- `getProvenance(contentId)` - View history

### 3.4 Treasury Contract
**Purpose:** Manage reward distribution

**Functions:**
- `distributeRewards(contributors, amounts)` - Distribute tokens
- `setBudget(amount)` - Set reward budget
- `getTreasuryBalance()` - Check balance

---

## Phase 4: Deployment (Week 7)

### 4.1 Testnet Deployment
- [ ] Deploy all contracts to testnet
- [ ] Test contributor flow
- [ ] Test reward distribution
- [ ] Test content verification

### 4.2 Mainnet Deployment
- [ ] Acquire mainnet tokens (if available)
- [ ] Deploy contracts to mainnet
- [ ] Configure oracle parameters
- [ ] Set initial treasury balance

---

## Phase 5: Integration (Week 8)

### 5.1 Website Integration
- [ ] Add Oracle UI to Compendium
- [ ] Connect wallet integration
- [ ] Implement contribution form
- [ ] Display verification badges

### 5.2 User Documentation
- [ ] Create contributor guide
- [ ] Write smart contract documentation
- [ ] Record video tutorials
- [ ] Set up support channel

---

## 📚 Essential Resources

### Official Documentation
- Alephium 2.0 Docs: https://docs.alephium.org/
- Smart Contract Guide: https://docs.alephium.org/smart-contracts/
- API Reference: https://docs.alephium.org/api/

### Developer Tools
- Alephium CLI: https://github.com/alephium/alephium-cli
- Wallet: https://wallet.alephium.org/
- Testnet Faucet: https://faucet.alephium.org/

### Community
- Discord: https://discord.gg/alephium
- GitHub Issues: https://github.com/alephium/alephium-node/issues
- Twitter: @alephium_org

---

## 🔐 Security Checklist

### Before Mainnet Deployment
- [ ] Security audit completed
- [ ] Testnet testing thorough (2+ weeks)
- [ ] Emergency pause mechanism
- [ ] Multi-sig treasury setup
- [ ] Recovery procedures documented
- [ ] Backup private keys stored offline

---

## 💡 Key Considerations

### Alephium 2.0 Differences
- **New smart contract syntax** (more like Solidity)
- **Better gas efficiency**
- **Enhanced oracle features**
- **Improved developer experience**

### Oracle System Design
- **Decentralized verification** (no single point of failure)
- **Token-based rewards** (incentivize contributions)
- **Chain-of-custody** (transparent provenance)
- **Community governance** (DAO for treasury management)

---

## 🎯 Immediate Next Steps

1. **Download Alephium 2.0 wallet**
2. **Get testnet tokens from faucet**
3. **Practice with testnet transactions**
4. **Study Alephium 2.0 smart contract docs**
5. **Design Oracle contract architecture**

---

**Date:** 2026-08-09
**Status:** Planning Phase
**Next:** Download wallet and get testnet tokens
