<template>
  <div class="card">
    <div class="card-title">角色图鉴</div>
    <div class="gallery">
      <div v-for="id in AGENT_IDS" :key="id" class="gallery-item">
        <img
          :src="AGENT_META[id].img"
          :style="{ borderColor: AGENT_META[id].color }"
          :alt="AGENT_META[id].display"
          @error="onAgentImgError($event, AGENT_META[id])"
        />
        <div>
          <div class="gallery-name" :style="{ color: AGENT_META[id].color }">
            {{ AGENT_META[id].display }}
          </div>
          <div class="gallery-role">{{ AGENT_META[id].role }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { AGENT_IDS, AGENT_META, onAgentImgError } from '../constants/agents.js'
</script>

<style scoped>
.gallery {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.gallery-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border: 1px solid var(--sao-border-dim);
}

.gallery-item img {
  width: 35px;
  height: 45px;
  object-fit: cover;
  border-radius: 4px;
  border: 2px solid;
}

.gallery-name {
  font-size: 0.85rem;
  font-weight: bold;
}

.gallery-role {
  font-size: 0.7rem;
  color: var(--muted);
}
</style>
