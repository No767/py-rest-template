env "dev" {
  src = "file://schema.sql"

  url = getenv("DATABASE_URL")

  dev = "docker://postgres/15/dev"
}