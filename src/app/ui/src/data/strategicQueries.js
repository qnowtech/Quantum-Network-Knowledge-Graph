/**
 * Strategic Queries from README.md
 * These queries can be executed against the Neo4j knowledge graph
 */

export const STRATEGIC_QUERIES = [
  {
    id: '1',
    title: 'People with Active Experience in a Specific Domain and Sector',
    question: 'Which people have active experience in "Quantum Machine Learning" and work in organizations in the "Finance" sector?',
    cypher: `MATCH (p:Person)-[:HAS_EXPERIENCE_IN]->(d:Domain),
      (p)-[:WORKS_AT]->(o:Organization)
WHERE d.name = "Quantum Machine Learning"
  AND o.industry_sector = "Finanzas"
  AND p.quantum_experience IN ["active", "exploration"]
RETURN p.name AS person,
       p.role AS role,
       o.name AS organization,
       o.industry_sector AS sector,
       d.name AS domain
ORDER BY person;`,
    parameters: {},
    description: 'Find experts in a specific domain working in a particular industry sector'
  },
  {
    id: '2',
    title: 'Organizations with "Business-Technology Gap" and Low Internal Capacity',
    question: 'Which organizations have the problem "Gap between business and technology" and don\'t have people with active experience in the domains that can solve it?',
    cypher: `MATCH (org:Organization)-[:HAS_PROBLEM]->(prob:Problem {name: "Gap entre negocio y tecnología"})
MATCH (prob)-[:CAN_BE_SOLVED_BY]->(d:Domain)
WHERE NOT EXISTS {
  MATCH (p:Person)-[:WORKS_AT]->(org),
        (p)-[:HAS_EXPERIENCE_IN]->(d)
  WHERE p.quantum_experience IN ["active", "exploration"]
}
RETURN org.name AS organization,
       prob.name AS problem,
       collect(DISTINCT d.name) AS relevant_domains;`,
    parameters: {},
    description: 'Identify organizations that need external expertise to solve their problems'
  },
  {
    id: '3',
    title: 'People Who Share Interests with a Given Person',
    question: 'Given a participant, who shares one or more domains of interest with that person?',
    cypher: `MATCH (p:Person {email: $email})-[:HAS_INTEREST]->(d:Domain)
MATCH (other:Person)-[:HAS_INTEREST]->(d)
WHERE other <> p
RETURN other.name AS potential_collaborator,
       collect(DISTINCT d.name) AS shared_domains
ORDER BY size(shared_domains) DESC;`,
    parameters: { email: '' },
    description: 'Find potential collaborators based on shared interests',
    requiresInput: true,
    inputLabel: 'Email address',
    inputPlaceholder: 'person@example.com'
  },
  {
    id: '4',
    title: 'Most Frequent Problems in the Ecosystem',
    question: 'What are the most frequent problems declared by people?',
    cypher: `MATCH (p:Person)-[:HAS_PROBLEM]->(prob:Problem)
RETURN prob.name AS problem,
       count(DISTINCT p) AS num_people
ORDER BY num_people DESC;`,
    parameters: {},
    description: 'Identify the most common challenges in the quantum computing ecosystem'
  },
  {
    id: '5',
    title: 'Domains with High Interest and Low Experience (Capability Gaps)',
    question: 'In which domains are there many interested people but few with active experience?',
    cypher: `MATCH (d:Domain)
OPTIONAL MATCH (p_int:Person)-[:HAS_INTEREST]->(d)
WITH d, count(DISTINCT p_int) AS interested
OPTIONAL MATCH (p_exp:Person)-[:HAS_EXPERIENCE_IN]->(d)
WITH d, interested, count(DISTINCT p_exp) AS experienced
RETURN d.name AS domain,
       interested,
       experienced,
       CASE
         WHEN experienced = 0 THEN interested * 1.0
         ELSE interested * 1.0 / experienced
       END AS interest_experience_ratio
ORDER BY interest_experience_ratio DESC, interested DESC;`,
    parameters: {},
    description: 'Find domains where there is high interest but limited practical experience'
  },
  {
    id: '6',
    title: 'Organizations with Expertise in Quantum Hardware',
    question: 'Which organizations have people with experience in quantum hardware?',
    cypher: `MATCH (o:Organization)<-[:WORKS_AT]-(p:Person)-[:HAS_EXPERIENCE_IN]->(d:Domain)
WHERE d.name = "Hardware cuántico"
RETURN o.name AS organization,
       collect(DISTINCT p.name) AS experts,
       count(DISTINCT p) AS num_experts
ORDER BY num_experts DESC;`,
    parameters: {},
    description: 'Find organizations with expertise in quantum hardware'
  },
  {
    id: '7',
    title: 'Pairs of People with Common Interests Working in Different Organizations',
    question: 'Which pairs of people share domains of interest but don\'t work in the same organization? (Potential cross-collaborations)',
    cypher: `MATCH (p1:Person)-[:HAS_INTEREST]->(d:Domain)<-[:HAS_INTEREST]-(p2:Person)
WHERE id(p1) < id(p2)
  AND NOT EXISTS {
    MATCH (p1)-[:WORKS_AT]->(o:Organization)<-[:WORKS_AT]-(p2)
  }
RETURN p1.name AS person_1,
       p2.name AS person_2,
       collect(DISTINCT d.name) AS shared_domains
ORDER BY size(shared_domains) DESC;`,
    parameters: {},
    description: 'Identify potential cross-organizational collaborations'
  }
];

