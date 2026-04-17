"""
Neo4j Schema for Drug Interaction Knowledge Graph
Run these Cypher queries to set up the production graph database
"""

NEO4J_SCHEMA = """
// ─────────────────────────────────────────────────────────────────
// CONSTRAINTS & INDEXES
// ─────────────────────────────────────────────────────────────────
CREATE CONSTRAINT drug_name_unique IF NOT EXISTS
  FOR (d:Drug) REQUIRE d.name IS UNIQUE;

CREATE CONSTRAINT enzyme_name_unique IF NOT EXISTS
  FOR (e:Enzyme) REQUIRE e.name IS UNIQUE;

CREATE INDEX drug_drugbank_idx IF NOT EXISTS
  FOR (d:Drug) ON (d.drugbank_id);

CREATE INDEX interaction_severity_idx IF NOT EXISTS
  FOR ()-[r:INTERACTS_WITH]-() ON (r.severity);

// ─────────────────────────────────────────────────────────────────
// DRUG NODES
// ─────────────────────────────────────────────────────────────────
MERGE (d:Drug {name: 'warfarin'})
SET d.drugbank_id = 'DB00682',
    d.half_life_hours = 37,
    d.protein_binding_pct = 99,
    d.therapeutic_class = 'Anticoagulant',
    d.narrow_therapeutic_index = true;

MERGE (d:Drug {name: 'simvastatin'})
SET d.drugbank_id = 'DB00641',
    d.half_life_hours = 2,
    d.protein_binding_pct = 95,
    d.therapeutic_class = 'Statin';

// ... (add all drugs similarly)

// ─────────────────────────────────────────────────────────────────
// ENZYME NODES
// ─────────────────────────────────────────────────────────────────
MERGE (e:Enzyme {name: 'CYP3A4'})
SET e.full_name = 'Cytochrome P450 3A4',
    e.location = 'liver, intestine',
    e.percentage_drugs_metabolized = 50;

MERGE (e:Enzyme {name: 'CYP2C9'})
SET e.full_name = 'Cytochrome P450 2C9',
    e.location = 'liver',
    e.percentage_drugs_metabolized = 15;

// ─────────────────────────────────────────────────────────────────
// DRUG-ENZYME RELATIONSHIPS
// ─────────────────────────────────────────────────────────────────
MATCH (d:Drug {name: 'warfarin'}), (e:Enzyme {name: 'CYP2C9'})
MERGE (d)-[:IS_SUBSTRATE_OF {affinity: 'high'}]->(e);

MATCH (d:Drug {name: 'fluconazole'}), (e:Enzyme {name: 'CYP2C9'})
MERGE (d)-[:INHIBITS {strength: 'strong', ki_uM: 0.5}]->(e);

MATCH (d:Drug {name: 'clarithromycin'}), (e:Enzyme {name: 'CYP3A4'})
MERGE (d)-[:INHIBITS {strength: 'strong', ki_uM: 0.8}]->(e);

// ─────────────────────────────────────────────────────────────────
// DRUG-DRUG INTERACTION EDGES
// ─────────────────────────────────────────────────────────────────
MATCH (a:Drug {name: 'warfarin'}), (b:Drug {name: 'aspirin'})
MERGE (a)-[r:INTERACTS_WITH {
  severity: 'Major',
  mechanism: 'pharmacodynamic',
  mechanism_detail: 'Additive anticoagulant + antiplatelet; GI mucosal damage',
  clinical_risk: 'Significant bleeding risk',
  recommendation: 'Avoid or use lowest aspirin dose with close INR monitoring',
  severity_score: 8.5,
  pubmed_ids: ['PMC2921255', '15009162'],
  drugbank_ref: 'DB00682-DB00945'
}]->(b);

MATCH (a:Drug {name: 'simvastatin'}), (b:Drug {name: 'clarithromycin'})
MERGE (a)-[r:INTERACTS_WITH {
  severity: 'Contraindicated',
  mechanism: 'CYP3A4_inhibition',
  mechanism_detail: 'CYP3A4 inhibition causes >10-fold simvastatin AUC increase',
  clinical_risk: 'Rhabdomyolysis and acute renal failure',
  recommendation: 'Contraindicated. Suspend simvastatin during clarithromycin course.',
  severity_score: 9.8,
  pubmed_ids: ['16216125'],
  drugbank_ref: 'DB00641-DB01211'
}]->(b);

// ─────────────────────────────────────────────────────────────────
// QUERY EXAMPLES
// ─────────────────────────────────────────────────────────────────

// Find all interactions for a drug:
// MATCH (d:Drug {name: 'warfarin'})-[r:INTERACTS_WITH]-(other:Drug)
// RETURN d.name, other.name, r.severity, r.mechanism
// ORDER BY r.severity_score DESC;

// Find contraindicated pairs in a medication list:
// WITH ['warfarin', 'aspirin', 'simvastatin', 'clarithromycin'] AS meds
// MATCH (a:Drug)-[r:INTERACTS_WITH {severity: 'Contraindicated'}]-(b:Drug)
// WHERE a.name IN meds AND b.name IN meds
// RETURN a.name, b.name, r.clinical_risk;

// Find enzyme interaction pathway:
// MATCH (a:Drug {name: 'fluconazole'})-[:INHIBITS]->(e:Enzyme)<-[:IS_SUBSTRATE_OF]-(b:Drug)
// RETURN a.name + ' inhibits ' + e.name + ' which metabolizes ' + b.name AS pathway;
"""

NEO4J_DOCKER_COMPOSE = """
version: '3.8'
services:
  neo4j:
    image: neo4j:5.18-community
    environment:
      NEO4J_AUTH: neo4j/mediguard2026
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_security_procedures_unrestricted: apoc.*
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
volumes:
  neo4j_data:
  neo4j_logs:
"""

print("Neo4j schema ready. Run with: docker-compose up neo4j")
print("Browser: http://localhost:7474  |  Bolt: bolt://localhost:7687")
