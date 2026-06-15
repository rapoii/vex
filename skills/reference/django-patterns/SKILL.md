---
name: django-patterns
description: Build Django apps with service boundaries, ORM discipline, migrations, DRF, and security defaults.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: reference
  triggers: ["Django models/views", "DRF APIs", "Migrations or settings"]
---

# Django Patterns

Patterns for scalable, maintainable Django and Django Rest Framework (DRF) applications.

## When to Activate

- Creating or modifying Django Models.
- Writing Views or API endpoints.
- Optimizing ORM queries.
- Managing database migrations.

## Core Principles

### 1. Fat Models, Skinny Views
Business logic belongs in Models or Services, not Views. Views should only handle HTTP logic (parsing request, returning response).

**Bad (Logic in View):**
```python
def publish_article(request, pk):
    article = Article.objects.get(pk=pk)
    if article.status != 'published':
        article.status = 'published'
        article.published_at = timezone.now()
        article.save()
        # send email logic...
    return HttpResponse('OK')
```

**Good (Logic in Model/Service):**
```python
class Article(models.Model):
    def publish(self):
        if self.status != 'published':
            self.status = 'published'
            self.published_at = timezone.now()
            self.save()
            send_publish_notification(self)

def publish_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.publish()
    return HttpResponse('OK')
```

### 2. Service Layer Pattern
For complex logic involving multiple models, use a Service layer rather than stuffing everything into one Model.

```python
# services.py
def create_user_with_profile(email, password, profile_data):
    with transaction.atomic():
        user = User.objects.create_user(email=email, password=password)
        Profile.objects.create(user=user, **profile_data)
        send_welcome_email(user)
    return user
```

### 3. ORM Optimization (N+1 Query Problem)
Always use `select_related` (for ForeignKeys) and `prefetch_related` (for ManyToMany or reverse ForeignKeys) when accessing related objects in a loop.

**Bad (N+1 queries):**
```python
books = Book.objects.all()
for book in books:
    print(book.author.name) # DB hit for EVERY book
```

**Good (2 queries):**
```python
books = Book.objects.select_related('author').all()
for book in books:
    print(book.author.name) # No extra DB hits
```

### 4. DRF Serializers
Use serializers strictly for data validation and representation. Avoid putting complex business logic in `create` or `update` methods if it can live in a service function.

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
```

### 5. Safe Migrations
- Never edit an applied migration file. Create a new one.
- Handle data migrations explicitly using `migrations.RunPython`.
- For large tables, avoid operations that lock the whole table (like adding a column with a default value without care in some DBs).

## Common Pitfalls

- **Leaking DB logic into templates**: Doing `{% for item in user.items.all %}` where `items` isn't prefetched causes N+1 queries during rendering.
- **Ignoring `transaction.atomic`**: Running multiple related database writes without a transaction. If one fails, data is left in an inconsistent state.
- **Exposing internal IDs**: Use UUIDs for public-facing URLs/APIs to prevent enumeration attacks, rather than sequential auto-incrementing IDs.

## Verification
- Do tests pass?
- Does `django-debug-toolbar` show a low number of queries?
- Are migrations reversible (if applicable)?
