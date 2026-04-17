"""
Knowledge Graph Service using NetworkX
Represents drug-enzyme-pathway relationships
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
import networkx as nx

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """
    In-memory knowledge graph using NetworkX.
    Represents drug nodes, enzyme nodes, pathway nodes, and interaction edges.
    Production: Replace with Neo4j for large-scale deployment.
    """
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._initialized = False
    
    async def initialize(self):
        """Build the drug interaction knowledge graph."""
        logger.info("Building drug knowledge graph...")
        self._build_graph()
        self._initialized = True
        logger.info(f"Knowledge graph ready: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
    
    def _build_graph(self):
        """Populate the knowledge graph with drug-enzyme-pathway data."""
        # ─── Drug Nodes ───
        drugs = [
            # (name, drugbank_id, half_life_hours, protein_binding_pct)
            ("warfarin", "DB00682", 37, 99),
            ("aspirin", "DB00945", 0.25, 30),
            ("simvastatin", "DB00641", 1.9, 95),
            ("atorvastatin", "DB01076", 14, 98),
            ("pravastatin", "DB00175", 1.8, 50),
            ("rosuvastatin", "DB01098", 19, 88),
            ("clopidogrel", "DB00758", 7.7, 98),
            ("omeprazole", "DB00338", 0.5, 95),
            ("pantoprazole", "DB00213", 1.0, 98),
            ("fluconazole", "DB00530", 30, 11),
            ("clarithromycin", "DB01211", 3, 70),
            ("amiodarone", "DB01118", 1008, 96),
            ("sertraline", "DB01104", 26, 98),
            ("phenelzine", "DB00780", 12, 0),
            ("lisinopril", "DB00722", 12, 0),
            ("spironolactone", "DB00421", 14, 90),
            ("metformin", "DB00331", 17, 0),
            ("ibuprofen", "DB01050", 2, 99),
            ("ciprofloxacin", "DB00537", 4, 40),
            ("oxycodone", "DB00497", 4, 45),
            ("diazepam", "DB00829", 43, 98),
            ("allopurinol", "DB00437", 1, 0),
            ("azathioprine", "DB00993", 3, 30),
            ("digoxin", "DB00390", 36, 25),
            ("lithium", "DB00317", 24, 0),
            ("amlodipine", "DB00381", 34, 97),
        ]
        
        for name, db_id, half_life, protein_binding in drugs:
            self.graph.add_node(
                name,
                node_type="drug",
                drugbank_id=db_id,
                half_life_hours=half_life,
                protein_binding_pct=protein_binding
            )
        
        # ─── Enzyme Nodes ───
        enzymes = [
            ("CYP2C9", "Cytochrome P450 2C9 - metabolizes ~15% of drugs"),
            ("CYP3A4", "Cytochrome P450 3A4 - metabolizes ~50% of drugs"),
            ("CYP2C19", "Cytochrome P450 2C19 - polymorphic enzyme"),
            ("CYP2D6", "Cytochrome P450 2D6 - highly polymorphic"),
            ("UGT", "UDP-glucuronosyltransferase - phase II conjugation"),
            ("P-gp", "P-glycoprotein - efflux transporter"),
            ("XO", "Xanthine oxidase - purine metabolism"),
        ]
        for name, desc in enzymes:
            self.graph.add_node(name, node_type="enzyme", description=desc)
        
        # ─── Drug-Enzyme Substrate/Inhibitor Relationships ───
        enzyme_relations = [
            # (drug, enzyme, relationship, effect_magnitude)
            ("warfarin", "CYP2C9", "substrate", "high"),
            ("warfarin", "CYP3A4", "substrate", "moderate"),
            ("simvastatin", "CYP3A4", "substrate", "high"),
            ("atorvastatin", "CYP3A4", "substrate", "moderate"),
            ("fluconazole", "CYP2C9", "inhibitor", "strong"),
            ("fluconazole", "CYP3A4", "inhibitor", "moderate"),
            ("clarithromycin", "CYP3A4", "inhibitor", "strong"),
            ("amiodarone", "CYP2C9", "inhibitor", "moderate"),
            ("amiodarone", "CYP3A4", "inhibitor", "moderate"),
            ("amiodarone", "P-gp", "inhibitor", "strong"),
            ("omeprazole", "CYP2C19", "inhibitor", "strong"),
            ("clopidogrel", "CYP2C19", "substrate", "high"),
            ("sertraline", "CYP2D6", "inhibitor", "moderate"),
            ("allopurinol", "XO", "inhibitor", "strong"),
            ("azathioprine", "XO", "substrate", "high"),
            ("digoxin", "P-gp", "substrate", "high"),
            ("amlodipine", "CYP3A4", "inhibitor", "weak"),
        ]
        
        for drug, enzyme, rel_type, magnitude in enzyme_relations:
            self.graph.add_edge(
                drug, enzyme,
                relationship=rel_type,
                magnitude=magnitude
            )
        
        # ─── Interaction Edges ───
        interactions = [
            ("warfarin", "aspirin", "pharmacodynamic", "Major"),
            ("warfarin", "fluconazole", "CYP2C9_inhibition", "Major"),
            ("warfarin", "amiodarone", "CYP2C9_CYP3A4_inhibition", "Major"),
            ("simvastatin", "clarithromycin", "CYP3A4_inhibition", "Contraindicated"),
            ("simvastatin", "amlodipine", "CYP3A4_inhibition", "Moderate"),
            ("sertraline", "phenelzine", "serotonin_syndrome", "Contraindicated"),
            ("lisinopril", "spironolactone", "hyperkalemia", "Major"),
            ("metformin", "ibuprofen", "renal_clearance", "Moderate"),
            ("ciprofloxacin", "amiodarone", "QT_prolongation", "Contraindicated"),
            ("oxycodone", "diazepam", "CNS_depression", "Major"),
            ("allopurinol", "azathioprine", "XO_inhibition", "Contraindicated"),
            ("digoxin", "amiodarone", "P-gp_inhibition", "Major"),
            ("clopidogrel", "omeprazole", "CYP2C19_inhibition", "Moderate"),
            ("lithium", "ibuprofen", "renal_clearance", "Major"),
        ]
        
        for drug_a, drug_b, mechanism, severity in interactions:
            self.graph.add_edge(
                drug_a, drug_b,
                relationship="INTERACTS_WITH",
                mechanism=mechanism,
                severity=severity
            )
    
    async def get_drug_interactions(self, drug_name: str) -> List[Dict[str, Any]]:
        """Get all known interactions for a drug."""
        drug = drug_name.lower().strip()
        if drug not in self.graph:
            return []
        
        results = []
        for neighbor in self.graph.neighbors(drug):
            edge_data = self.graph.get_edge_data(drug, neighbor)
            if edge_data:
                for key, data in edge_data.items():
                    if data.get("relationship") == "INTERACTS_WITH":
                        results.append({
                            "interacts_with": neighbor,
                            "mechanism": data.get("mechanism"),
                            "severity": data.get("severity")
                        })
        return results
    
    async def get_cyp_profile(self, drug_name: str) -> Dict[str, List[str]]:
        """Get CYP enzyme inhibitor/substrate profile for a drug."""
        drug = drug_name.lower().strip()
        profile = {"substrate": [], "inhibitor": [], "inducer": []}
        
        if drug not in self.graph:
            return profile
        
        for neighbor in self.graph.neighbors(drug):
            node_data = self.graph.nodes.get(neighbor, {})
            if node_data.get("node_type") == "enzyme":
                edge_data = self.graph.get_edge_data(drug, neighbor)
                if edge_data:
                    for _, data in edge_data.items():
                        rel = data.get("relationship", "")
                        if rel in profile:
                            profile[rel].append(neighbor)
        
        return profile
    
    async def find_interaction_path(self, drug_a: str, drug_b: str) -> Optional[List[str]]:
        """Find the enzyme/pathway mediating an interaction between two drugs."""
        a = drug_a.lower()
        b = drug_b.lower()
        
        try:
            path = nx.shortest_path(self.graph, a, b)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    async def get_graph_stats(self) -> Dict[str, Any]:
        """Return knowledge graph statistics."""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "drug_nodes": sum(1 for _, d in self.graph.nodes(data=True) if d.get("node_type") == "drug"),
            "enzyme_nodes": sum(1 for _, d in self.graph.nodes(data=True) if d.get("node_type") == "enzyme"),
            "interaction_edges": sum(1 for _, _, d in self.graph.edges(data=True) if d.get("relationship") == "INTERACTS_WITH"),
        }
    
    async def close(self):
        logger.info("Knowledge graph service closed.")
